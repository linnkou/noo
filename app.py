from flask import Flask, render_template, request, send_from_directory
import pandas as pd
import os

app = Flask(__name__)

# دالة لتصنيف التقدير بناءً على المعدل
def classify_grade(grade, grade_comments):
    if grade < 10:
        return grade_comments[0]
    elif 10 <= grade < 12:
        return grade_comments[1]
    elif 12 <= grade < 14:
        return grade_comments[2]
    elif 14 <= grade < 16:
        return grade_comments[3]
    elif 16 <= grade < 18:
        return grade_comments[4]
    elif 18 <= grade <= 20:
        return grade_comments[5]
    return "غير مصنف"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            # الحصول على ملف Excel المرفوع
            file = request.files['file']
            if file:
                # قراءة ملف Excel
                df = pd.read_excel(file)

                # الحصول على ملاحظات التقديرات من النموذج
                grade_comments = [
                    request.form.get('comment_0'),  # أقل من 10
                    request.form.get('comment_1'),  # من 10 إلى 11.99
                    request.form.get('comment_2'),  # من 12 إلى 13.99
                    request.form.get('comment_3'),  # من 14 إلى 15.99
                    request.form.get('comment_4'),  # من 16 إلى 17.99
                    request.form.get('comment_5')   # من 18 إلى 20
                ]

                # التأكد من وجود العمود "المعدل النهائي" في الملف
                if 'المعدل النهائي' in df.columns:
                    # إضافة عمود "التقدير" بناءً على المعدل النهائي
                    df['التقدير'] = df['المعدل النهائي'].apply(lambda x: classify_grade(x, grade_comments))

                    # حفظ الملف المعدل في مجلد "uploads"
                    os.makedirs("uploads", exist_ok=True)
                    output_path = os.path.join("uploads", "modified_" + file.filename)
                    df.to_excel(output_path, index=False)

                    return render_template('index.html', success=True, file_path=output_path)
                else:
                    return render_template('index.html', error="العمود 'المعدل النهائي' غير موجود في الملف.")
        except Exception as e:
            return render_template('index.html', error=f"حدث خطأ: {str(e)}")
    return render_template('index.html')

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory("uploads", filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
