# Python-Assignment

I referred to this document for performing the assessment: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html. It helped me with tasks such as making connections, copying, moving, creating, and uploading files.

<h2>list_s3_content Function </h2>
<pre>
def list_s3_content():
    try:
        response = s3.list_objects_v2(Bucket=S3_BUCKET)
        contents = response.get('Contents', [])
        return contents
    except Exception as e:
        flash(str(e))
        return []
</pre>
This function help to fetch the file or folder present in the bucket. It uses s3.list_objects_v2 to retrieve the contents of the S3 bucket and returns the list of objects.

<h2> Home page rendering</h2>
<pre>
@app.route('/')
def index():
    contents = list_s3_content()
    folders = get_folders(contents)
    return render_template('index.html', contents=contents, folders=folders)
</pre>
The index route serves as the homepage. It calls list_s3_content to get all the files and folders from the S3 bucket, and then get_folders to extract the folders. These values are passed to index.html for rendering the content on the page.

<h2>create_folder</h2>

<pre>
@app.route('/create-folder', methods=['POST'])
def create_folder():
    folder_name = request.form['folder_name']
    if folder_name:
        folder_name = folder_name.rstrip('/') + '/'
        try:
            s3.put_object(Bucket=S3_BUCKET, Key=folder_name)
            flash('Folder Created')
        except Exception as e:
            flash(str(e))
    return redirect(url_for('index'))
</pre>
It retrieves the folder_name from the form, ensures the folder name ends with a /, and then uses s3.put_object to create the folder in the S3 bucket.
Upon success or failure, a message is flashed, and the user is redirected to the homepage.

<h2> delete_object </h2>
<pre>
@app.route('/delete', methods=['POST'])
def delete_object():
    key = request.form['key']
    try:
        s3.delete_object(Bucket=S3_BUCKET, Key=key)
        flash('Deleted Successfully')
    except Exception as e:
        flash(str(e))
    return redirect(url_for('index'))
</pre>
It retrieves the key (object name) from the form and uses s3.delete_object to remove the object from the S3 bucket. Upon success or failure, a message is flashed, and the user is redirected to the homepage

<h2>move_copy_file</h2>

<pre>
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
            s3.delete_object(Bucket=S3_BUCKET, Key=src)
        flash(f'File {action} successfully from {src} to {dest}')
    except Exception as e:
        flash(f"Error: {str(e)}")
    return redirect(url_for('index'))
</pre>
It retrieves the source (src) and destination (dest) from the form. Depending on the selected action (move or copy), it either copies the file using s3.copy_object or moves it by copying and then deleting the source file.
Success or failure messages are flashed, and the user is redirected to the homepage
