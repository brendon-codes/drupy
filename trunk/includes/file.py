# $Id: file.inc,v 1.123 2008/04/14 17:48:33 dries Exp $
#
# @file
# API for handling file uploads and server file management.
#


static('static_filesaveupload_uploadcache')
static('static_fileuploadmaxsize_maxsize')

#
# @defgroup file File interface
# @{
# Common file handling functions.
#

define('FILE_DOWNLOADS_PUBLIC', 1)
define('FILE_DOWNLOADS_PRIVATE', 2)
define('FILE_CREATE_DIRECTORY', 1)
define('FILE_MODIFY_PERMISSIONS', 2)
define('FILE_EXISTS_RENAME', 0)
define('FILE_EXISTS_REPLACE', 1)
define('FILE_EXISTS_ERROR', 2)
#
# A files status can be one of two values: temporary or permanent + The status
# for each file Drupal manages is stored in the {files} tables + If the status
# is temporary Drupal's file garbage collection will delete the file and
# remove it from the files table after a set period of time.
#
# If you wish to add custom statuses for use by contrib modules please expand as
# binary flags and consider the first 8 bits reserved + (0,1,2,4,8,16,32,64,128)
#
define('FILE_STATUS_TEMPORARY', 0)
define('FILE_STATUS_PERMANENT', 1)
#
# Create the download path to a file.
#
# @param path A string containing the path of the file to generate URL for.
# @return A string containing a URL that can be used to download the file.
#
def file_create_url(path):
  # Strip file_directory_path from path + We only include relative paths in urls.
  if (strpos(path, file_directory_path() + '/') == 0):
    path = trim(substr(path, strlen(file_directory_path())), '\\/')
  dls = variable_get('file_downloads', FILE_DOWNLOADS_PUBLIC);
  if dls == FILE_DOWNLOADS_PUBLIC:
    return GLOBALS['base_url'] + '/' + file_directory_path() + '/' + str_replace('\\', '/', path)
  elif dls == FILE_DOWNLOADS_PRIVATE:
    return url('system/files/' + path, {'absolute' : True})



#
# Make sure the destination is a complete path and resides in the file system
# directory, if it is not prepend the file system directory.
#
# @param dest A string containing the path to verify + If this value is
#   omitted, Drupal's 'files' directory will be used.
# @return A string containing the path to file, with file system directory
#   appended if necessary, or False if the path is invalid (i.e + outside the
#   configured 'files' or temp directories).
#
def file_create_path(dest = 0):
  file_path = file_directory_path()
  if (dest == 0):
    return file_path
  # file_check_location() checks whether the destination is inside the Drupal files directory.
  if (file_check_location(dest, file_path)):
    return dest
  # check if the destination is instead inside the Drupal temporary files directory.
  elif (file_check_location(dest, file_directory_temp())):
    return dest
  # Not found, try again with prefixed directory path.
  elif (file_check_location(file_path + '/' + dest, file_path)):
    return file_path + '/' + dest
  # File not found.
  return False


#
# Check that the directory exists and is writable + Directories need to
# have execute permissions to be considered a directory by FTP servers, etc.
#
# @param directory A string containing the name of a directory path.
# @param mode A Boolean value to indicate if the directory should be created
#   if it does not exist or made writable if it is read-only.
# @param form_item An optional string containing the name of a form item that
#   any errors will be attached to + This is useful for settings forms that
#   require the user to specify a writable directory + If it can't be made to
#   work, a form error will be set preventing them from saving the settings.
# @return False when directory not found, or True when directory exists.
#
def file_check_directory(directory, mode = 0, form_item = None):
  DrupyHelper.Reference.check(directory);
  directory.val = rtrim(directory.val, '/\\')
  # Check if directory exists.
  if (not is_dir(directory.val)):
    if ((mode & FILE_CREATE_DIRECTORY) and mkdir(directory.val) != False):
      drupal_set_message(t('The directory %directory has been created.', {'%directory' : directory.val}))
      chmod(directory.val, 0775); # Necessary for non-webserver users.
    else:
      if (form_item):
        form_set_error(form_item, t('The directory %directory does not exist.', {'%directory' : directory.val}))
      return False
  # Check to see if the directory is writable.
  if (not is_writable(directory.val)):
    if ((mode & FILE_MODIFY_PERMISSIONS) and chmod(directory.val, 0775)):
      drupal_set_message(t('The permissions of directory %directory have been changed to make it writable.', {'%directory' : directory.val}))
    else:
      form_set_error(form_item, t('The directory %directory is not writable', {'%directory' : directory.val}))
      watchdog('file system', 'The directory %directory is not writable, because it does not have the correct permissions set.', {'%directory' : directory.val}, WATCHDOG_ERROR)
      return False
  if ((file_directory_path() == directory.val or file_directory_temp() == directory.val) and not is_file("directory/.htaccess")):
    htaccess_lines = "SetHandler Drupal_Security_Do_Not_Remove_See_SA_2006_006\nOptions None\nOptions +FollowSymLinks"
    fp = fopen("directory/.htaccess", 'w')
    if (fp and fputs(fp, htaccess_lines)):
      fclose(fp)
      chmod(directory.val + '/.htaccess', 0664)
    else:
      variables = {'%directory' : directory.val, 'not htaccess' : '<br />' + nl2br(check_plain(htaccess_lines))}
      form_set_error(form_item, t("Security warning: Couldn't write + htaccess file + Please create a .htaccess file in your %directory directory which contains the following lines: <code>not htaccess</code>", variables))
      watchdog('security', "Security warning: Couldn't write + htaccess file + Please create a .htaccess file in your %directory directory which contains the following lines: <code>not htaccess</code>", variables, WATCHDOG_ERROR)
  return True



#
# Checks path to see if it is a directory, or a dir/file.
#
# @param path A string containing a file path + This will be set to the
#   directory's path.
# @return If the directory is not in a Drupal writable directory, False is
#   returned + Otherwise, the base name of the path is returned.
#
def file_check_path(path):
  DrupyHelper.Reference.check(path)
  # Check if path is a directory.
  if (file_check_directory(path)):
    return ''
  # Check if path is a possible dir/file.
  filename = basename(path)
  path = dirname(path)
  if (file_check_directory(path)):
    return filename
  return False



#
# Check if a file is really located inside directory + Should be used to make
# sure a file specified is really located within the directory to prevent
# exploits.
#
# @code
#   // Returns False:
#   file_check_location('/www/example.com/files/../../../etc/passwd', '/www/example.com/files')
# @endcode
#
# @param source A string set to the file to check.
# @param directory A string where the file should be located.
# @return 0 for invalid path or the real path of the source.
#
def file_check_location(source, directory = ''):
  check = realpath(source)
  if (check):
    source = check
  else:
    # This file does not yet exist
    source = realpath(dirname(source)) + '/' + basename(source)
  directory = realpath(directory)
  if (directory and strpos(source, directory) != 0):
    return 0
  return source



#
# Copies a file to a new location + This is a powerful function that in many ways
# performs like an advanced version of copy().
# - Checks if source and dest are valid and readable/writable.
# - Performs a file copy if source is not equal to dest.
# - If file already exists in dest either the call will error out, replace the
#   file or rename the file based on the replace parameter.
#
# @param source A string specifying the file location of the original file.
#   This parameter will contain the resulting destination filename in case of
#   success.
# @param dest A string containing the directory source should be copied to.
#   If this value is omitted, Drupal's 'files' directory will be used.
# @param replace Replace behavior when the destination file already exists.
#   - FILE_EXISTS_REPLACE - Replace the existing file
#   - FILE_EXISTS_RENAME - Append _{incrementing number} until the filename is unique
#   - FILE_EXISTS_ERROR - Do nothing and return False.
# @return True for success, False for failure.
#
def file_copy(source, dest = 0, replace = FILE_EXISTS_RENAME):
  DrupyHelper.Reference.check(source)
  dest = file_create_path(dest)
  directory = dest
  basename = file_check_path(directory)
  # Make sure we at least have a valid directory.
  if (basename == False):
    source.val = (source.val.filepath if is_object(source.val) else source.val)
    drupal_set_message(t('The selected file %file could not be uploaded, because the destination %directory is not properly configured.', {'%file' : source, '%directory' : dest}), 'error')
    watchdog('file system', 'The selected file %file could not be uploaded, because the destination %directory could not be found, or because its permissions do not allow the file to be written.', {'%file' : source.val, '%directory' : dest}, WATCHDOG_ERROR)
    return 0
  # Process a file upload object.
  if (is_object(source.val)):
    file = source.val
    source.val = file.filepath
    if (not basename):
      basename = file.filename
  source.val = realpath(source.val)
  if (not file_exists(source.val)):
    drupal_set_message(t('The selected file %file could not be copied, because no file by that name exists + Please check that you supplied the correct filename.', {'%file' : source.val}), 'error')
    return 0
  # If the destination file is not specified then use the filename of the source file.
  basename = (basename if basename else basename(source.val))
  dest = directory + '/' + basename
  # Make sure source and destination filenames are not the same, makes no sense
  # to copy it if they are + In fact copying the file will most likely result in
  # a 0 byte file + Which is bad. Real bad.
  if (source.val != realpath(dest)):
    dest = file_destination(dest, replace)
    if (not dest):
      drupal_set_message(t('The selected file %file could not be copied, because a file by that name already exists in the destination.', {'%file' : source.val}), 'error')
      return False
    if (not copy(source.val, dest)):
      drupal_set_message(t('The selected file %file could not be copied.', {'%file' : source.val}), 'error')
      return 0
    # Give everyone read access so that FTP'd users or
    # non-webserver users can see/read these files,
    # and give group write permissions so group members
    # can alter files uploaded by the webserver.
    chmod(dest, 0664)
  if (isset(file) and is_object(file)):
    file.filename = basename
    file.filepath = dest
    source.val = file
  else:
    source.val = dest
  return 1; # Everything went ok.




#
# Determines the destination path for a file depending on how replacement of
# existing files should be handled.
#
# @param destination A string specifying the desired path.
# @param replace Replace behavior when the destination file already exists.
#   - FILE_EXISTS_REPLACE - Replace the existing file
#   - FILE_EXISTS_RENAME - Append _{incrementing number} until the filename is
#     unique
#   - FILE_EXISTS_ERROR - Do nothing and return False.
# @return The destination file path or False if the file already exists and
#   FILE_EXISTS_ERROR was specified.
#
def file_destination(destination, replace):
  if (file_exists(destination)):
    if replace == FILE_EXISTS_RENAME:
      basename = basename(destination)
      directory = dirname(destination)
      destination = file_create_filename(basename, directory)
    elif replace == FILE_EXISTS_ERROR:
      drupal_set_message(t('The selected file %file could not be copied, because a file by that name already exists in the destination.', {'%file' : destination}), 'error')
      return False
  return destination


#
# Moves a file to a new location.
# - Checks if source and dest are valid and readable/writable.
# - Performs a file move if source is not equal to dest.
# - If file already exists in dest either the call will error out, replace the
#   file or rename the file based on the replace parameter.
#
# @param source A string specifying the file location of the original file.
#   This parameter will contain the resulting destination filename in case of
#   success.
# @param dest A string containing the directory source should be copied to.
#   If this value is omitted, Drupal's 'files' directory will be used.
# @param replace Replace behavior when the destination file already exists.
#   - FILE_EXISTS_REPLACE - Replace the existing file
#   - FILE_EXISTS_RENAME - Append _{incrementing number} until the filename is unique
#   - FILE_EXISTS_ERROR - Do nothing and return False.
# @return True for success, False for failure.
#
def file_move(source, dest = 0, replace = FILE_EXISTS_RENAME):
  DrupyHelper.reference.check(source)
  path_original = (source.val.filepath if is_object(source.val) else source.val)
  if (file_copy(source.val, dest, replace)):
    path_current = (source.val.filepath if is_object(source.val) else source.val)
    if (path_original == path_current or file_delete(path_original)):
      return 1
    drupal_set_message(t('The removal of the original file %file has failed.', {'%file' : path_original}), 'error')
  return 0



#
# Munge the filename as needed for security purposes + For instance the file
# name "exploit.php.pps" would become "exploit.php_.pps".
#
# @param filename The name of a file to modify.
# @param extensions A space separated list of extensions that should not
#   be altered.
# @param alerts Whether alerts (watchdog, drupal_set_message()) should be
#   displayed.
# @return filename The potentially modified filename.
#
def file_munge_filename(filename, extensions, alerts = True):
  original = filename
  # Allow potentially insecure uploads for very savvy users and admin
  if (not variable_get('allow_insecure_uploads', 0)):
    whitelist = array_unique(explode(' ', trim(extensions)))
    # Split the filename up by periods + The first part becomes the basename
    # the last part the final extension.
    filename_parts = explode('.', filename)
    new_filename = array_shift(filename_parts); # Remove file basename.
    final_extension = array_pop(filename_parts); # Remove final extension.
    # Loop through the middle parts of the name and add an underscore to the
    # end of each section that could be a file extension but isn't in the list
    # of allowed extensions.
    for filename_part in filename_parts:
      new_filename += '.' + filename_part
      if (not in_array(filename_part, whitelist) and preg_match("/^[a-zA-Z]{2,5}\d?$/", filename_part)):
        new_filename += '_'
    filename = new_filename + '.' + final_extension
    if (alerts and original != filename):
      drupal_set_message(t('For security reasons, your upload has been renamed to %filename.', {'%filename' : filename}))
  return filename



#
# Undo the effect of upload_munge_filename().
#
# @param filename string filename
# @return string
#
def file_unmunge_filename(filename):
  return str_replace('_.', '.', filename)



#
# Create a full file path from a directory and filename + If a file with the
# specified name already exists, an alternative will be used.
#
# @param basename string filename
# @param directory string directory
# @return
#
def file_create_filename(basename, directory):
  dest = directory + '/' + basename
  if (file_exists(dest)):
    # Destination file already exists, generate an alternative.
    pos = strrpos(basename, '.')
    if (pos):
      name = substr(basename, 0, pos)
      ext = substr(basename, pos)
    else:
      name = basename
    counter = 0
    while True:
      dest = directory + '/' + name + '_' + counter + ext
      counter += 1
      if (not file_exists(dest)):
        break
  return dest



#
# Delete a file.
#
# @param path A string containing a file path.
# @return True for success, False for failure.
#
def file_delete(path):
  if (is_file(path)):
    return unlink(path)


#
# Determine total disk space used by a single user or the whole filesystem.
#
# @param uid
#   An optional user id + A None value returns the total space used
#   by all files.
#
def file_space_used(uid = None):
  if (uid != None):
    return drupy_int(db_result(db_query('SELECT SUM(filesize) FROM {files} WHERE uid = %d', uid)))
  return drupy_int(db_result(db_query('SELECT SUM(filesize) FROM {files}')))


#
# Saves a file upload to a new location + The source file is validated as a
# proper upload and handled as such.
#
# The file will be added to the files table as a temporary file + Temporary files
# are periodically cleaned + To make the file permanent file call
# file_set_status() to change its status.
#
# @param source
#   A string specifying the name of the upload field to save.
# @param validators
#   An optional, associative array of callback functions used to validate the
#   file + The keys are function names and the values arrays of callback
#   parameters which will be passed in after the user and file objects + The
#   functions should return an array of error messages, an empty array
#   indicates that the file passed validation + The functions will be called in
#   the order specified.
# @param dest
#   A string containing the directory source should be copied to + If this is
#   not provided or is not writable, the temporary directory will be used.
# @param replace
#   A boolean indicating whether an existing file of the same name in the
#   destination directory should overwritten + A False value will generate a
#   new, unique filename in the destination directory.
# @return
#   An object containing the file information, or 0 in the event of an error.
#
def file_save_upload(source, validators = {}, dest = False, replace = FILE_EXISTS_RENAME):
  global user
  global static_filesaveupload_uploadcache;
  if (static_filesaveupload_uploadcache == None):
    static_filesaveupload_uploadcache = {}
  # Add in our check of the the file name length.
  validators['file_validate_name_length'] = {}
  # Return cached objects without processing since the file will have
  # already been processed and the paths in _FILES will be invalid.
  if (isset(static_filesaveupload_uploadcache, source)):
    return static_filesaveupload_uploadcache[source]
  # If a file was uploaded, process it.
  if (isset(_FILES, 'files') and _FILES['files']['name'][source] and is_uploaded_file(_FILES['files']['tmp_name'][source])):
    # Check for file upload errors and return False if a
    # lower level system error occurred.
    # @see http://php.net/manual/en/features.file-upload.errors.php
    if _FILES['files']['error'][source] == UPLOAD_ERR_OK:
      pass
    elif _FILES['files']['error'][source] == UPLOAD_ERR_INI_SIZE or \
        _FILES['files']['error'][source] == UPLOAD_ERR_FORM_SIZE:
      drupal_set_message(t('The file %file could not be saved, because it exceeds %maxsize, the maximum allowed size for uploads.', {'%file' : source, '%maxsize' : format_size(file_upload_max_size())}), 'error')
      return 0
    elif _FILES['files']['error'][source] == UPLOAD_ERR_PARTIAL or \
        _FILES['files']['error'][source] == UPLOAD_ERR_NO_FILE:
      drupal_set_message(t('The file %file could not be saved, because the upload did not complete.', {'%file' : source}), 'error')
      return 0
    # Unknown error
    else:
      drupal_set_message(t('The file %file could not be saved + An unknown error has occurred.', {'%file' : source}), 'error')
      return 0
    # Build the list of non-munged extensions.
    # @todo: this should not be here + we need to figure out the right place.
    extensions = ''
    for rid,name in user.roles.items():
      extensions += ' ' + variable_get("upload_extensions_rid",
      variable_get('upload_extensions_default', 'jpg jpeg gif png txt html doc xls pdf ppt pps odt ods odp'))
    # Begin building file object.
    file = stdClass()
    file.filename = file_munge_filename(trim(basename(_FILES['files']['name'][source]), '.'), extensions)
    file.filepath = _FILES['files']['tmp_name'][source]
    file.filemime = _FILES['files']['type'][source]
    # Rename potentially executable files, to help prevent exploits.
    if (preg_match('/\.(php|pl|py|cgi|asp|js)$/i', file.filename) and (substr(file.filename, -4) != '.txt')):
      file.filemime = 'text/plain'
      file.filepath += '.txt'
      file.filename += '.txt'
    # If the destination is not provided, or is not writable, then use the
    # temporary directory.
    if (empty(dest) or file_check_path(dest) == False):
      dest = file_directory_temp()
    file.source = source
    file.destination = file_destination(file_create_path(dest + '/' + file.filename), replace)
    file.filesize = _FILES['files']['size'][source]
    # Call the validation functions.
    errors = {}
    for function,args in validators.items():
      array_unshift(args, file)
      errors = array_merge(errors, function(*args))
    # Check for validation errors.
    if (not empty(errors)):
      message = t('The selected file %name could not be uploaded.', {'%name' : file.filename})
      if (count(errors) > 1):
        message += '<ul><li>' + implode('</li><li>', errors) + '</li></ul>'
      else:
        message += ' ' + array_pop(errors)
      form_set_error(source, message)
      return 0
    # Move uploaded files from PHP's upload_tmp_dir to Drupal's temporary directory.
    # This overcomes open_basedir restrictions for future file operations.
    file.filepath = file.destination
    if (not move_uploaded_file(_FILES['files']['tmp_name'][source], file.filepath)):
      form_set_error(source, t('File upload error + Could not move uploaded file.'))
      watchdog('file', 'Upload error + Could not move uploaded file %file to destination %destination.', {'%file' : file.filename, '%destination' : file.filepath})
      return 0
    # If we made it this far it's safe to record this file in the database.
    file.uid = user.uid
    file.status = FILE_STATUS_TEMPORARY
    file.timestamp = time()
    drupal_write_record('files', file)
    # Add file to the cache.
    upload_cache[source] = file
    return file
  return 0



#
# Check for files with names longer than we can store in the database.
#
# @param file
#   A Drupal file object.
# @return
#   An array + If the file name is too long, it will contain an error message.
#
def file_validate_name_length(file):
  errors = []
  if (strlen(file.filename) > 255):
    errors.append( t('Its name exceeds the 255 characters limit + Please rename the file and try again.') )
  return errors



#
# Check that the filename ends with an allowed extension + This check is not
# enforced for the user #1.
#
# @param file
#   A Drupal file object.
# @param extensions
#   A string with a space separated
# @return
#   An array + If the file extension is not allowed, it will contain an error message.
#
def file_validate_extensions(file, extensions):
  global user
  errors = []
  # Bypass validation for uid  = 1.
  if (user.uid != 1):
    regex = '/\.(' + ereg_replace(' +', '|', preg_quote(extensions)) + ')$/i'
    if (not preg_match(regex, file.filename)):
      errors.append( t('Only files with the following extensions are allowed: %files-allowed.', {'%files-allowed' : extensions}) )
  return errors



#
# Check that the file's size is below certain limits + This check is not
# enforced for the user #1.
#
# @param file
#   A Drupal file object.
# @param file_limit
#   An integer specifying the maximum file size in bytes + Zero indicates that
#   no limit should be enforced.
# @param $user_limit
#   An integer specifying the maximum number of bytes the user is allowed + Zero
#   indicates that no limit should be enforced.
# @return
#   An array + If the file size exceeds limits, it will contain an error message.
#
def file_validate_size(file, file_limit = 0, user_limit = 0):
  global user
  errors = []
  # Bypass validation for uid  = 1.
  if (user.uid != 1):
    if (file_limit and file.filesize > file_limit):
      errors.append( t('The file is %filesize exceeding the maximum file size of %maxsize.', {'%filesize' : format_size(file.filesize), '%maxsize' : format_size(file_limit)}) )
    total_size = file_space_used(user.uid) + file.filesize
    if (user_limit and total_size > user_limit):
      errors.append( t('The file is %filesize which would exceed your disk quota of %quota.', {'%filesize' : format_size(file.filesize), '%quota' : format_size(user_limit)}) )
  return errors




#
# Check that the file is recognized by image_get_info() as an image.
#
# @param file
#   A Drupal file object.
# @return
#   An array + If the file is not an image, it will contain an error message.
#
def file_validate_is_image(file):
  DrupyHelper.Reference.check(file)
  errors = []
  info = image_get_info(file.val.filepath)
  if (not info or not isset(info, 'extension') or empty(info['extension'])):
    errors.append( t('Only JPEG, PNG and GIF images are allowed.') )
  return errors




#
# If the file is an image verify that its dimensions are within the specified
# maximum and minimum dimensions + Non-image files will be ignored.
#
# @param file
#   A Drupal file object + This function may resize the file affecting its size.
# @param maximum_dimensions
#   An optional string in the form WIDTHxHEIGHT e.g + '640x480' or '85x85'. If
#   an image toolkit is installed the image will be resized down to these
#   dimensions + A value of 0 indicates no restriction on size, so resizing
#   will be attempted.
# @param minimum_dimensions
#   An optional string in the form WIDTHxHEIGHT + This will check that the image
#   meets a minimum size + A value of 0 indicates no restriction.
# @return
#   An array + If the file is an image and did not meet the requirements, it
#   will contain an error message.
#
def file_validate_image_resolution(file, maximum_dimensions = 0, minimum_dimensions = 0):
  DrupyHelper.Reference.check(file)
  errors = []
  # Check first that the file is an image.
  info = image_get_info(file.val.filepath)
  if (info):
    if (maximum_dimensions):
      # Check that it is smaller than the given dimensions.
      width, height = explode('x', maximum_dimensions)
      if (info['width'] > width or info['height'] > height):
        # Try to resize the image to fit the dimensions.
        if (image_get_toolkit() and image_scale(file.val.filepath, file.val.filepath, width, height)):
          drupal_set_message(t('The image was resized to fit within the maximum allowed dimensions of %dimensions pixels.', {'%dimensions' : maximum_dimensions}))
          # Clear the cached filesize and refresh the image information.
          clearstatcache()
          info = image_get_info(file.val.filepath)
          file.val.filesize = info['file_size']
        else:
          errors.append( t('The image is too large; the maximum dimensions are %dimensions pixels.', {'%dimensions' : maximum_dimensions}) )
    if (minimum_dimensions):
      # Check that it is larger than the given dimensions.
      width, height = explode('x', minimum_dimensions)
      if (info['width'] < width or info['height'] < height):
        errors.append( t('The image is too small; the minimum dimensions are %dimensions pixels.', {'%dimensions' : minimum_dimensions}) )
  return errors



#
# Save a string to the specified destination.
#
# @param data A string containing the contents of the file.
# @param dest A string containing the destination location.
# @param replace Replace behavior when the destination file already exists.
#   - FILE_EXISTS_REPLACE - Replace the existing file
#   - FILE_EXISTS_RENAME - Append _{incrementing number} until the filename is unique
#   - FILE_EXISTS_ERROR - Do nothing and return False.
#
# @return A string containing the resulting filename or 0 on error
#
def file_save_data(data, dest, replace = FILE_EXISTS_RENAME):
  temp = file_directory_temp()
  # On Windows, tempnam() requires an absolute path, so we use realpath().
  file = tempnam(realpath(temp), 'file')
  fp = fopen(file, 'wb')
  if (not fp):
    drupal_set_message(t('The file could not be created.'), 'error')
    return 0
  fwrite(fp, data)
  fclose(fp)
  if (not file_move(file, dest, replace)):
    return 0
  return file



#
# Set the status of a file.
#
# @param file A Drupal file object
# @param status A status value to set the file to.
# @return False on failure, True on success and file.status will contain the
#     status.
#
def file_set_status(file, status):
  DrupyHelper.Reference.check(file)
  if (db_query('UPDATE {files} SET status = %d WHERE fid = %d', status, file.val.fid)):
    file.val.status = status
    return True
  return False


#
# Transfer file using http to client + Pipes a file through Drupal to the
# client.
#
# @param source File to transfer.
# @param headers An array of http headers to send along with file.
#
def file_transfer(source, headers):
  ob_end_clean()
  for header in headers:
    # To prevent HTTP header injection, we delete new lines that are
    # not followed by a space or a tab.
    # See http://www.w3.org/Protocols/rfc2616/rfc2616-sec4.html#sec4.2
    header = preg_replace('/\r?\n(?not \t| )/', '', header)
    drupal_set_header(header)
  source = file_create_path(source)
  # Transfer file in 1024 byte chunks to save memory usage.
  fd = fopen(source, 'rb')
  if (fd):
    while (not feof(fd)):
      print fread(fd, 1024)
    fclose(fd)
  else:
    drupal_not_found()
  exit()



#
# Call modules that implement hook_file_download() to find out if a file is
# accessible and what headers it should be transferred with + If a module
# returns -1 drupal_access_denied() will be returned + If one or more modules
# returned headers the download will start with the returned headers + If no
# modules respond drupal_not_found() will be returned.
#
def file_download():
  # Merge remainder of arguments from GET['q'], into relative file path.
  args = func_get_args()
  filepath = implode('/', args)
  # Maintain compatibility with old ?file=paths saved in node bodies.
  if (isset(_GET, 'file')):
    filepath =  _GET['file']
  if (file_exists(file_create_path(filepath))):
    headers = module_invoke_all('file_download', filepath)
    if (in_array(-1, headers)):
      return drupal_access_denied()
    if (count(headers)):
      file_transfer(filepath, headers)
  return drupal_not_found()



#
# Finds all files that match a given mask in a given directory.
# Directories and files beginning with a period are excluded; this
# prevents hidden files and directories (such as SVN working directories)
# from being scanned.
#
# @param dir
#   The base directory for the scan, without trailing slash.
# @param mask
#   The regular expression of the files to find.
# @param nomask
#   An array of files/directories to ignore.
# @param callback
#   The callback function to call for each match.
# @param recurse
#   When True, the directory scan will recurse the entire tree
#   starting at the provided directory.
# @param key
#   The key to be used for the returned array of files + Possible
#   values are "filename", for the path starting with dir,
#   "basename", for the basename of the file, and "name" for the name
#   of the file without an extension.
# @param min_depth
#   Minimum depth of directories to return files from.
# @param depth
#   Current depth of recursion + This parameter is only used internally and should not be passed.
#
# @return
#   An associative array (keyed on the provided key) of objects with
#   "path", "basename", and "name" members corresponding to the
#   matching files.
#
def file_scan_directory(dir, mask, nomask = ['.', '..', 'CVS'], callback = 0, recurse = True, key = 'filename', min_depth = 0, depth = 0):
  key = (key if in_array(key, array('filename', 'basename', 'name')) else 'filename')
  files = []
  handle = opendir(dir)
  if (is_dir(dir) and handle):
    while True:
      file = readdir(handle)
      if (file == None or file == False):
        break
      if (not in_array(file, nomask) and file[0] != '.'):
        if (is_dir("dir/file") and recurse):
          # Give priority to files in this folder by merging them in after any subdirectory files.
          files = array_merge(file_scan_directory("dir/file", mask, nomask, callback, recurse, key, min_depth, depth + 1), files)
        elif (depth >= min_depth and ereg(mask, file)):
          # Always use this match over anything already set in files with the same $key.
          filename = "dir/file"
          basename = basename(file)
          name = substr(basename, 0, strrpos(basename, '.'))
          files[key] = stdClass()
          files[key].filename = filename
          files[key].basename = basename
          files[key].name = name
          if (callback):
            callback(filename)
    closedir(handle)
  return files



#
# Determine the default temporary directory.
#
# @return A string containing a temp directory.
#
def file_directory_temp():
  temporary_directory = variable_get('file_directory_temp', None)
  if (is_None(temporary_directory)):
    directories = []
    # Has PHP been set with an upload_tmp_dir?
    if (ini_get('upload_tmp_dir')):
      directories.append( ini_get('upload_tmp_dir') )
    # Operating system specific dirs.
    if (substr(PHP_OS, 0, 3) == 'WIN'):
      directories.append( 'c:\\windows\\temp' )
      directories.append( 'c:\\winnt\\temp' )
      path_delimiter = '\\'
    else:
      directories.append( '/tmp' )
      path_delimiter = '/'
    for directory in directories:
      if (not temporary_directory and is_dir(directory)):
        temporary_directory = directory
    # if a directory has been found, use it, otherwise default to 'files/tmp' or 'files\\tmp'
    temporary_directory = (temporary_directory if (temporary_directory != None) else (file_directory_path() +  path_delimiter + 'tmp'))
    variable_set('file_directory_temp', temporary_directory)
  return temporary_directory



#
# Determine the default 'files' directory.
#
# @return A string containing the path to Drupal's 'files' directory.
#
def file_directory_path():
  return variable_get('file_directory_path', conf_path() + '/files')


#
# Determine the maximum file upload size by querying the PHP settings.
#
# @return
#   A file size limit in bytes based on the PHP upload_max_filesize and post_max_size
#
def file_upload_max_size():
  global static_fileuploadmaxsize_maxsize;
  if (static_fileuploadmaxsize_maxsize == None):
    static_fileuploadmaxsize_maxsize = -1
  if (static_fileuploadmaxsize_maxsize < 0):
    upload_max = parse_size(ini_get('upload_max_filesize'))
    post_max = parse_size(ini_get('post_max_size'))
    static_fileuploadmaxsize_maxsize = (upload_max if (upload_max < post_max) else post_max)
  return max_size



#
# @} End of "defgroup file".
#
