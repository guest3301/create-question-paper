from flask import Flask, request, send_file
from helpers.paper import QuestionPaper
from helpers.html import indexHTML
import os, subprocess, threading

app = Flask(__name__)

def run_serveo():
    command = ["ssh", "-R", "80:localhost:3301", "serveo.net"]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    for line in process.stdout:
        if "Forwarding HTTP traffic from" in line:
            print(line.strip())

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        class_name = request.form['class_name']
        subject = request.form['subject']
        term = request.form['term']
        total_marks = request.form['total_marks']
        template_path = 'template.docx'
        output_path = os.path.join(os.getcwd(), f"Question paper {class_name} ({subject}) [{term}].docx")
        question_paper = QuestionPaper(template_path, output_path, global_font_size=12)
        question_paper.replace_placeholders(class_name, subject, term, total_marks)
        num_sections = int(request.form['num_sections'])
        for i in range(num_sections):
            heading_text = request.form[f'section_{i}_heading']
            marks = request.form[f'section_{i}_marks']
            blank_lines = int(request.form[f'section_{i}_blank_lines'])
            questions, question_images, answer_lines = [], [], []
            num_questions = int(request.form[f'section_{i}_num_questions'])
            for j in range(num_questions):
                question_text = request.form[f'section_{i}_question_{j}_text']
                questions.append(question_text)
                image_path = request.files.get(f'section_{i}_question_{j}_image')
                if image_path and image_path.filename:
                    image_filename = f"uploads/{image_path.filename}"
                    image_path.save(image_filename)
                    question_images.append(image_filename)
                else:
                    question_images.append(None)
                add_answer_line = request.form.get(f'section_{i}_question_{j}_answer_line') == 'yes'
                answer_lines.append(add_answer_line)
            question_paper.add_section(
                heading_text=heading_text,
                questions=questions,
                marks=marks,
                question_images=question_images,
                font_size=12,
                blank_lines=blank_lines,
                answer_lines=answer_lines
            )
        question_paper.save()
        return send_file(output_path, as_attachment=True)
    return indexHTML

if __name__ == '__main__':
    threading.Thread(target=run_serveo).start()
    os.makedirs('uploads', exist_ok=True)
    app.run(debug=False, port=3301, host='0.0.0.0')