from flask import Flask, render_template, request, redirect, url_for, flash
import boto3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

AWS_ACCESS_KEY = ''
AWS_SECRET_ACCESS_KEY = ''
REGION = 'eu-north-1'
S3_BUCKET = 'vikaskarbail'


s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=REGION
)

def list_s3_content():
    try:
        response = s3.list_objects_v2(Bucket=S3_BUCKET)
        contents = response.get('Contents', [])
        return contents

    except Exception as e:
        flash(str(e))
        return []

def get_folders(contents):
    folders = set()
    for item in contents:
        key = item['Key']
        if key.endswith('/'):
            folders.add(key)
    # return folders
    return sorted(folders)


@app.route('/')
def index():
    contents = list_s3_content()
    folders = get_folders(contents)
    # return render_template('index.html)
    return render_template('index.html', contents=contents, folders=folders)


@app.route('/create-folder', methods=['POST'])
def create_folder():
    folder_name = request.form['folder_name']
    if folder_name:
        # folder_name = folder_name.rstrip('/')
        folder_name = folder_name.rstrip('/') + '/'
        try:
            s3.put_object(Bucket=S3_BUCKET, Key=folder_name)
            flash('Folder Created')
            # print("Folder Created...")
        except Exception as e:
            flash(str(e))
    return redirect(url_for('index'))


@app.route('/delete', methods=['POST'])
def delete_object():
    key = request.form['key']
    try:
        s3.delete_object(Bucket=S3_BUCKET, Key=key)
        # print("Deleted..")
        flash('Deleted Sucessfully')
    except Exception as e:
        flash(str(e))
    return redirect(url_for('index'))
 

@app.route('/upload', methods=['POST'])
def upload_file():
    folder = request.form.get('folder')
    if 'file' not in request.files:
        # print("Folder doesn't exit")
        flash('No file part')
        return redirect(url_for('index'))

    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('index'))

    if folder:
        file_key = f"{folder}{file.filename}"
    else:
        file_key = file.filename

    try:
        s3.upload_fileobj(file, S3_BUCKET, file_key)
        # print("Uploaded")
        flash('File uploaded successfully')
    except Exception as e:
        flash(str(e))

    return redirect(url_for('index'))


@app.route('/move-copy', methods=['POST'])
def move_copy_file():
    src = request.form['src']
    dest = request.form['dest']
    action = request.form['action']

    try:
        if not src or not dest:
            flash('Source and Destination keys must be provided')
            return redirect(url_for('index'))
        s3.copy_object(Bucket=S3_BUCKET, CopySource={'Bucket': S3_BUCKET, 'Key': src}, Key=dest)
        if action == 'move':
            # print(action)
            s3.delete_object(Bucket=S3_BUCKET, Key=src)

        flash(f'File {action} successfully from {src} to {dest}')
    except Exception as e:
        flash(f"Error: {str(e)}")
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
