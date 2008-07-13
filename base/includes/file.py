#!/usr/bin/env python
# $Id: file.inc,v 1.126 2008/06/18 03:36:23 dries Exp $

"""
  API for handling file uploads and server file management.

  @package includes
  @see <a href='http://drupy.net'>Drupy Homepage</a>
  @see <a href='http://drupal.org'>Drupal Homepage</a>
  @note Drupy is a port of the Drupal project.
  @note This file was ported from Drupal's includes/file.inc
  @author Brendon Crawford
  @copyright 2008 Brendon Crawford
  @contact message144 at users dot sourceforge dot net
  @created 2008-01-10
  @version 0.1
  @note License:

    This program is free software; you can redistribute it and/or
    modify it under the terms of the GNU General Public License
    as published by the Free Software Foundation; either version 2
    of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to:
    
    The Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor,
    Boston, MA  02110-1301,
    USA
"""

__version__ = "$Revision: 1 $"

from lib.drupy import DrupyPHP as php

#
# Common file handling functions.
#

#
# Flag to indicate that the 'public' file download method is enabled.
#
# When using this method, files are available from a regular HTTP request,
# which provides no additional access restrictions.
#
FILE_DOWNLOADS_PUBLIC = 1

#
# Flag to indicate that the 'private' file download method is enabled.
#
# When using this method, all file requests are served by Drupal, during which
# access-control checking can be performed.
#
FILE_DOWNLOADS_PRIVATE = 2

#
# Flag used by file_create_directory() -- create directory if not present.
#
FILE_CREATE_DIRECTORY = 1

#
# Flag used by file_create_directory() -- file permissions may be changed.
#
FILE_MODIFY_PERMISSIONS = 2

#
# Flag for dealing with existing files: Append number until filename is unique.
#
FILE_EXISTS_RENAME = 0

#
# Flag for dealing with existing files: Replace the existing file.
#
FILE_EXISTS_REPLACE = 1

#
# Flag for dealing with existing files: Do nothing and return FALSE.
#
FILE_EXISTS_ERROR = 2

#
# File status -- File has been temporarily saved to the {files} tables.
#
# Drupal's file garbage collection will delete the file and remove it from the
# files table after a set period of time.
#
FILE_STATUS_TEMPORARY = 0

#
# File status -- File has been permanently saved to the {files} tables.
#
# If you wish to add custom statuses for use by contrib plugins please expand
# as binary flags and consider the first 8 bits reserved.
# (0,1,2,4,8,16,32,64,128).
#
FILE_STATUS_PERMANENT = 1

def file_create_url(path):
  """
   Create the download path to a file.
  
   @param path A string containing the path of the file to generate URL for.
   @return A string containing a URL that can be used to download the file.
  """
  # Strip file_directory_path from path + We only include relative paths in urls.
  if (php.strpos(path, file_directory_path() + '/') == 0):
    path = php.trim(php.substr(path, php.strlen(file_directory_path())), '\\/')
  dls = variable_get('file_downloads', FILE_DOWNLOADS_PUBLIC);
  if dls == FILE_DOWNLOADS_PUBLIC:
    return GLOBALS['base_url'] + '/' + file_directory_path() + '/' + \
      php.str_replace('\\', '/', path)
  elif dls == FILE_DOWNLOADS_PRIVATE:
    return url('system/files/' + path, {'absolute' : True})



def file_create_path(dest = 0):
  """
   Make sure the destination is a complete path and resides in the file system
   directory, if it is not prepend the file system directory.
  
   @param dest A string containing the path to verify + If this value is
     omitted, Drupal's 'files' directory will be used.
   @return A string containing the path to file, with file system directory
     appended if necessary, or False if the path is invalid (i.e + outside the
     configured 'files' or temp directories).
  """
  file_path = file_directory_path()
  if (dest == 0):
    return file_path
  # file_check_location() checks whether the destination is inside the
  # Drupal files directory.
  if (file_check_location(dest, file_path)):
    return dest
  # check if the destination is instead inside the Drupal temporary
  # files directory.
  elif (file_check_location(dest, file_directory_temp())):
    return dest
  # Not found, try again with prefixed directory path.
  elif (file_check_location(file_path + '/' + dest, file_path)):
    return file_path + '/' + dest
  # File not found.
  return False


def file_check_directory(directory, mode = 0, form_item = None):
  """
   Check that the directory exists and is writable + Directories need to
   have execute permissions to be considered a directory by FTP servers, etc.
  
   @param directory A string containing the name of a directory path.
   @param mode A Boolean value to indicate if the directory should be created
     if it does not exist or made writable if it is read-only.
   @param form_item An optional string containing the name of a form item that
     any errors will be attached to + This is useful for settings forms that
     require the user to specify a writable directory + If it can't be made to
     work, a form error will be set preventing them from saving the settings.
   @return False when directory not found, or True when directory exists.
  """
  php.Reference.check(directory);
  directory._ = php.rtrim(directory._, '/\\')
  # Check if directory exists.
  if (not php.is_dir(directory._)):
    if ((mode & FILE_CREATE_DIRECTORY) and mkdir(directory._) != False):
      drupal_set_message(t('The directory %directory has been created.', \
        {'%directory' : directory._}))
      chmod(directory._, 0775); # Necessary for non-webserver users.
    else:
      if (form_item):
        form_set_error(form_item, \
          t('The directory %directory does not exist.', \
          {'%directory' : directory._}))
      return False
  # Check to see if the directory is writable.
  if (not php.is_writable(directory._)):
    if ((mode & FILE_MODIFY_PERMISSIONS) and chmod(directory._, 0775)):
      drupal_set_message(t('The permissions of directory %directory ' + \
        'have been changed to make it writable.', \
        {'%directory' : directory._}))
    else:
      form_set_error(form_item, t('The directory %directory is not writable', \
        {'%directory' : directory._}))
      watchdog('file system', 'The directory %directory is not writable, ' + \
        'because it does not have the correct permissions set.', \
        {'%directory' : directory._}, WATCHDOG_ERROR)
      return False
  if ((file_directory_path() == directory._ or \
      file_directory_temp() == directory._) and \
      not php.is_file("directory/.htaccess")):
    htaccess_lines = \
      "SetHandler Drupal_Security_Do_Not_Remove_See_SA_2006_006\n" + \
      "Options None\nOptions +FollowSymLinks"
    fp = fopen("directory/.htaccess", 'w')
    if (fp and fputs(fp, htaccess_lines)):
      fclose(fp)
      chmod(directory._ + '/.htaccess', 0664)
    else:
      variables = {'%directory' : directory._, \
        '!htaccess' : '<br />' + php.nl2br(check_plain(htaccess_lines))}
      form_set_error(form_item, t("Security warning: " + \
        "Couldn't write + htaccess file. " + \
        "Please create a .htaccess file in your " + \
        "%directory directory which contains the following lines: " + \
        "<code>!htaccess</code>", variables))
      watchdog('security', "Security warning: Couldn't write " + \
        ".htaccess file. Please create a .htaccess file in " + \
        "your %directory directory which contains the " + \
        "following lines: <code>not htaccess</code>", \
        variables, WATCHDOG_ERROR)
  return True



def file_check_path(path):
  """
   Checks path to see if it is a directory, or a dir/file.
  
   @param path A string containing a file path + This will be set to the
     directory's path.
   @return If the directory is not in a Drupal writable directory, False is
     returned + Otherwise, the base name of the path is returned.
  """
  php.Reference.check(path)
  # Check if path is a directory.
  if (file_check_directory(path)):
    return ''
  # Check if path is a possible dir/file.
  filename = basename(path)
  path = php.dirname(path)
  if (file_check_directory(path)):
    return filename
  return False



def file_check_location(source, directory = ''):
  """
   Check if a file is really located inside directory + Should be used to make
   sure a file specified is really located within the directory to prevent
   exploits.
  
   @code
     // Returns False:
     file_check_location('/www/example.com/files/../../../etc/passwd', \
       '/www/example.com/files')
   @endcode
  
   @param source A string set to the file to check.
   @param directory A string where the file should be located.
   @return FALSE for invalid path or the real path of the source.
  """
  check = realpath(source)
  if (check):
    source = check
  else:
    # This file does not yet exist
    source = realpath(php.dirname(source)) + '/' + basename(source)
  directory = realpath(directory)
  if (directory and php.strpos(source, directory) != 0):
    return False
  return source



def file_copy(source, dest = 0, replace = FILE_EXISTS_RENAME):
  """
   Copies a file to a new location.
   This is a powerful function that in many ways
   performs like an advanced version of copy().
   - Checks if source and dest are valid and readable/writable.
   - Performs a file copy if source is not equal to dest.
   - If file already exists in dest either the call will
     error out, replace the
     file or rename the file based on the replace parameter.
  
   @param source A string specifying the file location of the original file.
     This parameter will contain the resulting destination filename in case of
     success.
   @param dest A string containing the directory source should be copied to.
     If this value is omitted, Drupal's 'files' directory will be used.
   @param replace Replace behavior when the destination file already exists.
     - FILE_EXISTS_REPLACE - Replace the existing file
     - FILE_EXISTS_RENAME - Append _{incrementing number} until
       the filename is unique
     - FILE_EXISTS_ERROR - Do nothing and return False.
   @return True for success, False for failure.
  """
  php.Reference.check(source)
  dest = file_create_path(dest)
  directory = dest
  basename = file_check_path(directory)
  # Make sure we at least have a valid directory.
  if (basename == False):
    if hasattr(source, 'filepath'):
      source._ = source.filepath
    drupal_set_message(t('The selected file %file could not be ' + \
      'uploaded, because the destination %directory is not ' + \
      'properly configured.', \
      {'%file' : source._, '%directory' : dest}), 'error')
    watchdog('file system', 'The selected file %file could not ' + \
      'be uploaded, because the destination %directory could ' + \
      'not be found, or because its permissions do ' + \
      'not allow the file to be written.', \
      {'%file' : source._, '%directory' : dest}, WATCHDOG_ERROR)
    return False
  # Process a file upload object.
  if (php.is_object(source._)):
    file = source._
    source._ = file.filepath
    if (not basename):
      basename = file.filename
  source._ = php.realpath(source._)
  if (not php.file_exists(source._)):
    drupal_set_message(t('The selected file %file could not be copied, ' + \
      'because no file by that name exists. ' + \
      'Please check that you supplied the correct filename.', \
      {'%file' : source._}), 'error')
    return False
  # If the destination file is not specified then use the filename
  # of the source file.
  basename = (basename if basename else basename(source._))
  dest._ = directory + '/' + basename
  # Make sure source and destination filenames are not the same, makes no sense
  # to copy it if they are + In fact copying the file will most
  # likely result in
  # a 0 byte file + Which is bad. Real bad.
  if (source._ != php.realpath(dest._)):
    dest._ = file_destination(dest._, replace)
    if (not dest._):
      drupal_set_message(t('The selected file %file could not be copied, ' + \
        'because a file by that name already exists in the destination.', \
        {'%file' : source._}), 'error')
      return False
    if (not copy(source._, dest._)):
      drupal_set_message(t('The selected file %file could not be copied.', \
        {'%file' : source._}), 'error')
      return False
    # Give everyone read access so that FTP'd users or
    # non-webserver users can see/read these files,
    # and give group write permissions so group members
    # can alter files uploaded by the webserver.
    chmod(dest._, 0664)
  if (php.isset(file) and php.is_object(file)):
    file.filename = basename
    file.filepath = dest._
    source._ = file
  else:
    source._ = dest
  return True # Everything went ok.



def file_destination(destination, replace):
  """
   Determines the destination path for a file depending on how replacement of
   existing files should be handled.
  
   @param destination A string specifying the desired path.
   @param replace Replace behavior when the destination file already exists.
     - FILE_EXISTS_REPLACE - Replace the existing file
     - FILE_EXISTS_RENAME - Append _{incrementing number} until the filename is
       unique
     - FILE_EXISTS_ERROR - Do nothing and return False.
   @return The destination file path or False if the file already exists and
     FILE_EXISTS_ERROR was specified.
  """
  if (php.file_exists(destination)):
    if replace == FILE_EXISTS_RENAME:
      basename = basename(destination)
      directory = php.dirname(destination)
      destination = file_create_filename(basename, directory)
    elif replace == FILE_EXISTS_ERROR:
      drupal_set_message(t('The selected file %file could not be copied, \
        because a file by that name already exists in the destination.', \
        {'%file' : destination}), 'error')
      return False
  return destination


def file_move(source, dest = 0, replace = FILE_EXISTS_RENAME):
  """
   Moves a file to a new location.
   - Checks if source and dest are valid and readable/writable.
   - Performs a file move if source is not equal to dest.
   - If file already exists in dest either the call will error out, replace the
     file or rename the file based on the replace parameter.
  
   @param source A string specifying the file location of the original file.
     This parameter will contain the resulting destination filename in case of
     success.
   @param dest A string containing the directory source should be copied to.
     If this value is omitted, Drupal's 'files' directory will be used.
   @param replace Replace behavior when the destination file already exists.
     - FILE_EXISTS_REPLACE - Replace the existing file
     - FILE_EXISTS_RENAME - Append _{incrementing number} until the
       filename is unique
     - FILE_EXISTS_ERROR - Do nothing and return False.
   @return True for success, False for failure.
  """
  php.Reference.check(source)
  if hasattr(source, 'filepath'):
    source._ = source.filepath
  path_original = source._
  if (file_copy(source._, dest, replace)):
    path_current = (source.filepath if hasattr(source, 'filepath') else \
      source._)
    if (path_original == path_current or file_delete(path_original)):
      return True
    drupal_set_message(t('The removal of the original file %file ' + \
      'has failed.', {'%file' : path_original}), 'error')
  return False



def file_munge_filename(filename, extensions, alerts = True):
  """
   Munge the filename as needed for security purposes + For instance the file
   name "exploit.php.pps" would become "exploit.php_.pps".
  
   @param filename The name of a file to modify.
   @param extensions A space separated list of extensions that should not
     be altered.
   @param alerts Whether alerts (watchdog, drupal_set_message()) should be
     displayed.
   @return filename The potentially modified filename.
  """
  original = filename
  # Allow potentially insecure uploads for very savvy users and admin
  if (not variable_get('allow_insecure_uploads', 0)):
    whitelist = array_unique(php.explode(' ', php.trim(extensions)))
    # Split the filename up by periods + The first part becomes the basename
    # the last part the final extension.
    filename_parts = php.explode('.', filename)
    new_filename = php.array_shift(filename_parts); # Remove file basename.
    final_extension = php.array_pop(filename_parts); # Remove final extension.
    # Loop through the middle parts of the name and add an underscore to the
    # end of each section that could be a file extension but isn't in the list
    # of allowed extensions.
    for filename_part in filename_parts:
      new_filename += '.' + filename_part
      if (not php.in_array(filename_part, whitelist) and \
          php.preg_match("/^[a-zA-Z]{2,5}\d?$/", filename_part)):
        new_filename += '_'
    filename = new_filename + '.' + final_extension
    if (alerts and original != filename):
      drupal_set_message(t('For security reasons, your upload has ' + \
        'been renamed to %filename.', {'%filename' : filename}))
  return filename



def file_unmunge_filename(filename):
  """
   Undo the effect of upload_munge_filename().
  
   @param filename string filename
   @return string
  """
  return php.str_replace('_.', '.', filename)



def file_create_filename(basename, directory):
  """
   Create a full file path from a directory and filename + If a file with the
   specified name already exists, an alternative will be used.
  
   @param basename string filename
   @param directory string directory
   @return
  """
  dest = directory + '/' + basename
  if (php.file_exists(dest)):
    # Destination file already exists, generate an alternative.
    pos = strrpos(basename, '.')
    if (pos):
      name = php.substr(basename, 0, pos)
      ext = php.substr(basename, pos)
    else:
      name = basename
    counter = 0
    while True:
      dest = directory + '/' + name + '_' + counter + ext
      counter += 1
      if (not php.file_exists(dest)):
        break
  return dest



def file_delete(path):
  """
   Delete a file.
  
   @param path A string containing a file path.
   @return True for success, False for failure.
  """
  if (php.is_file(path)):
    return p.unlink(path)


def file_space_used(uid = None):
  """
   Determine total disk space used by a single user or the whole filesystem.
  
   @param uid
     An optional user id + A None value returns the total space used
     by all files.
  """
  if (uid != None):
    return drupy_int(db_result(db_query(\
      'SELECT SUM(filesize) FROM {files} WHERE uid = %d', uid)))
  return drupy_int(db_result(db_query('SELECT SUM(filesize) FROM {files}')))


def file_save_upload(source, validators = {}, dest = False, \
    replace = FILE_EXISTS_RENAME):
  """
   Saves a file upload to a new location + The source file is validated as a
   proper upload and handled as such.
  
   The file will be added to the files table as a temporary file.
   Temporary files
   are periodically cleaned + To make the file permanent file call
   file_set_status() to change its status.
  
   @param source
     A string specifying the name of the upload field to save.
   @param validators
     An optional, associative array of callback functions used to validate the
     file + The keys are function names and the values arrays of callback
     parameters which will be passed in after the user and file objects + The
     functions should return an array of error messages, an empty array
     indicates that the file passed validation.
     The functions will be called in
     the order specified.
   @param dest
     A string containing the directory source should be copied to + If this is
     not provided or is not writable, the temporary directory will be used.
   @param replace
     A boolean indicating whether an existing file of the same name in the
     destination directory should overwritten + A False value will generate a
     new, unique filename in the destination directory.
   @return
     An object containing the file information, or False
     in the event of an error.
  """
  php.static(file_save_upload, 'upload_cache', {})
  # Add in our check of the the file name length.
  validators['file_validate_name_length'] = {}
  # Return cached objects without processing since the file will have
  # already been processed and the paths in FILES will be invalid.
  if (php.isset(file_save_upload.uploadcache, source)):
    return file_save_upload.uploadcache[source]
  # If a file was uploaded, process it.
  if (php.isset(p.FILES, 'files') and p.FILES['files']['name'][source] and \
      php.is_uploaded_file(p.FILES['files']['tmp_name'][source])):
    # Check for file upload errors and return False if a
    # lower level system error occurred.
    # @see http://php.net/manual/en/features.file-upload.errors.php
    if p.FILES['files']['error'][source] == UPLOAD_ERR_OK:
      pass
    elif p.FILES['files']['error'][source] == UPLOAD_ERR_INI_SIZE or \
        p.FILES['files']['error'][source] == UPLOAD_ERR_FORM_SIZE:
      drupal_set_message(t(\
        'The file %file could not be saved, because it exceeds %maxsize, ' + \
        'the maximum allowed size for uploads.', \
        {'%file' : source, '%maxsize' : \
        format_size(file_upload_max_size())}), 'error')
      return False
    elif p.FILES['files']['error'][source] == UPLOAD_ERR_PARTIAL or \
        p.FILES['files']['error'][source] == UPLOAD_ERR_NO_FILE:
      drupal_set_message(t('The file %file could not be saved, ' + \
        'because the upload did not complete.', {'%file' : source}), 'error')
      return False
    # Unknown error
    else:
      drupal_set_message(t('The file %file could not be saved. ' + \
        'An unknown error has occurred.', {'%file' : source}), 'error')
      return False
    # Build the list of non-munged extensions.
    # @todo: this should not be here + we need to figure out the right place.
    extensions = ''
    for rid,name in user.roles.items():
      extensions += ' ' + variable_get("upload_extensions_rid",
      variable_get('upload_extensions_default', \
        'jpg jpeg gif png txt html doc xls pdf ppt pps odt ods odp'))
    # Begin building file object.
    file = php.stdClass()
    file.filename = file_munge_filename(php.trim(\
      basename(p.FILES['files']['name'][source]), '.'), extensions)
    file.filepath = p.FILES['files']['tmp_name'][source]
    file.filemime = p.FILES['files']['type'][source]
    # Rename potentially executable files, to help prevent exploits.
    if (php.preg_match('/\.(php|pl|py|cgi|asp|js)$/i', file.filename) and \
        (php.substr(file.filename, -4) != '.txt')):
      file.filemime = 'text/plain'
      file.filepath += '.txt'
      file.filename += '.txt'
    # If the destination is not provided, or is not writable, then use the
    # temporary directory.
    if (php.empty(dest) or file_check_path(dest) == False):
      dest = file_directory_temp()
    file.source = source
    file.destination = file_destination(file_create_path(dest + '/' + \
      file.filename), replace)
    file.filesize = FILES['files']['size'][source]
    # Call the validation functions.
    errors = {}
    for function,args in validators.items():
      array_unshift(args, file)
      errors = php.array_merge(errors, function(*args))
    # Check for validation errors.
    if (not php.empty(errors)):
      message = t('The selected file %name could not be uploaded.', \
        {'%name' : file.filename})
      if (php.count(errors) > 1):
        message += '<ul><li>' + php.implode('</li><li>', errors) + '</li></ul>'
      else:
        message += ' ' + php.array_pop(errors)
      form_set_error(source, message)
      return False
    # Move uploaded files from PHP's upload_tmp_dir to
    # Drupal's temporary directory.
    # This overcomes open_basedir restrictions for future file operations.
    file.filepath = file.destination
    if (not move_uploaded_file(p.FILES['files']['tmp_name'][source], \
        file.filepath)):
      form_set_error(source, t('File upload error. ' + \
        'Could not move uploaded file.'))
      watchdog('file', 'Upload error + Could not move uploaded file ' + \
        '%file to destination %destination.', \
        {'%file' : file.filename, '%destination' : file.filepath})
      return False
    # If we made it this far it's safe to record this file in the database.
    file.uid = user.uid
    file.status = FILE_STATUS_TEMPORARY
    file.timestamp = time()
    drupal_write_record('files', file)
    # Add file to the cache.
    file_save_upload.upload_cache[source] = file
    return file
  return False



def file_validate_name_length(file):
  """
   Check for files with names longer than we can store in the database.
  
   @param file
     A Drupal file object.
   @return
     An array + If the file name is too long, it will contain an error message.
  """
  errors = []
  if (php.strlen(file.filename) > 255):
    errors.append( t('Its name exceeds the 255 characters limit. ' + \
      'Please rename the file and try again.') )
  return errors



def file_validate_extensions(file, extensions):
  """
   Check that the filename ends with an allowed extension + This check is not
   enforced for the user #1.
  
   @param file
     A Drupal file object.
   @param extensions
     A string with a space separated
   @return
     An array + If the file extension is not allowed,
     it will contain an error message.
  """
  errors = []
  # Bypass validation for uid  = 1.
  if (lib_bootstrap.user.uid != 1):
    regex = '/\.(' + ereg_replace(' +', '|', \
      php.preg_quote(extensions)) + ')$/i'
    if (not php.preg_match(regex, file.filename)):
      errors.append( t('Only files with the following extensions ' + \
        'are allowed: %files-allowed.', {'%files-allowed' : extensions}) )
  return errors



def file_validate_size(file, file_limit = 0, user_limit = 0):
  """
   Check that the file's size is below certain limits + This check is not
   enforced for the user #1.
  
   @param file
     A Drupal file object.
   @param file_limit
     An integer specifying the maximum file size in bytes.
     Zero indicates that
     no limit should be enforced.
   @param $user_limit
     An integer specifying the maximum number of bytes the user is allowed .
     Zero indicates that no limit should be enforced.
   @return
     An array + If the file size exceeds limits,
     it will contain an error message.
  """
  errors = []
  # Bypass validation for uid  = 1.
  if (lib_bootstrap.user.uid != 1):
    if (file_limit and file.filesize > file_limit):
      errors.append( t('The file is %filesize exceeding the ' + \
        'maximum file size of %maxsize.', \
        {'%filesize' : format_size(file.filesize), \
        '%maxsize' : format_size(file_limit)}) )
    total_size = file_space_used(user.uid) + file.filesize
    if (user_limit and total_size > user_limit):
      errors.append( t('The file is %filesize which would exceed ' + \
        'your disk quota of %quota.', \
        {'%filesize' : format_size(file.filesize), \
        '%quota' : format_size(user_limit)}) )
  return errors




def file_validate_is_image(file):
  """
   Check that the file is recognized by image_get_info() as an image.
  
   @param file
     A Drupal file object.
   @return
     An array + If the file is not an image, it will contain an error message.
  """
  errors = []
  info = image_get_info(file.filepath)
  if (not info or not php.isset(info, 'extension') or \
      php.empty(info['extension'])):
    errors.append( t('Only JPEG, PNG and GIF images are allowed.') )
  return errors




def file_validate_image_resolution(file, maximum_dimensions = 0, \
    minimum_dimensions = 0):
  """
   If the file is an image verify that its dimensions are within the specified
   maximum and minimum dimensions + Non-image files will be ignored.
  
   @param file
     A Drupal file object + This function may resize the file
     affecting its size.
   @param maximum_dimensions
     An optional string in the form WIDTHxHEIGHT e.g + '640x480' or '85x85'. If
     an image toolkit is installed the image will be resized down to these
     dimensions + A value of 0 indicates no restriction on size, so resizing
     will be attempted.
   @param minimum_dimensions
     An optional string in the form WIDTHxHEIGHT.
     This will check that the image
     meets a minimum size + A value of 0 indicates no restriction.
   @return
     An array + If the file is an image and did not meet the requirements, it
     will contain an error message.
  """
  php.Reference.check(file)
  errors = []
  # Check first that the file is an image.
  info = image_get_info(file.filepath)
  if (info):
    if (maximum_dimensions):
      # Check that it is smaller than the given dimensions.
      width, height = php.explode('x', maximum_dimensions)
      if (info['width'] > width or info['height'] > height):
        # Try to resize the image to fit the dimensions.
        if (image_get_toolkit() and image_scale(file.filepath, \
            file.filepath, width, height)):
          drupal_set_message(t('The image was resized to fit within ' + \
            'the maximum allowed dimensions of %dimensions pixels.', \
            {'%dimensions' : maximum_dimensions}))
          # Clear the cached filesize and refresh the image information.
          clearstatcache()
          info = image_get_info(file.filepath)
          file.filesize = info['file_size']
        else:
          errors.append( t('The image is too large; the maximum ' + \
            'dimensions are %dimensions pixels.', \
            {'%dimensions' : maximum_dimensions}) )
    if (minimum_dimensions):
      # Check that it is larger than the given dimensions.
      width, height = php.explode('x', minimum_dimensions)
      if (info['width'] < width or info['height'] < height):
        errors.append( t('The image is too small; the ' + \
          'minimum dimensions are %dimensions pixels.', \
          {'%dimensions' : minimum_dimensions}) )
  return errors



def file_save_data(data, dest, replace = FILE_EXISTS_RENAME):
  """
   Save a string to the specified destination.
  
   @param data A string containing the contents of the file.
   @param dest A string containing the destination location.
   @param replace Replace behavior when the destination file already exists.
     - FILE_EXISTS_REPLACE - Replace the existing file
     - FILE_EXISTS_RENAME - Append _{incrementing number}
       until the filename is unique
     - FILE_EXISTS_ERROR - Do nothing and return False.
  
   @return A string containing the resulting filename or False on error
  """
  temp = file_directory_temp()
  # On Windows, tempnam() requires an absolute path, so we use realpath().
  file = tempnam(realpath(temp), 'file')
  fp = p.fopen(file, 'wb')
  if (not fp):
    drupal_set_message(t('The file could not be created.'), 'error')
    return False
  p.fwrite(fp, data)
  p.fclose(fp)
  if (not file_move(file, dest, replace)):
    return False
  return file



def file_set_status(file, status):
  """
   Set the status of a file.
  
   @param file A Drupal file object
   @param status A status value to set the file to.
   @return False on failure, True on success and file.status will contain the
       status.
  """
  php.Reference.check(file)
  if (db_query('UPDATE {files} SET status = %d WHERE fid = %d', \
      status, file.fid)):
    file.status = status
    return True
  return False


def file_transfer(source, headers):
  """
   Transfer file using http to client + Pipes a file through Drupal to the
   client.
  
   @param source File to transfer.
   @param headers An array of http headers to send along with file.
  """
  ob_end_clean()
  for php.header in headers:
    # To prevent HTTP php.header injection, we delete new lines that are
    # not followed by a space or a tab.
    # See http://www.w3.org/Protocols/rfc2616/rfc2616-sec4.html#sec4.2
    php.header = php.preg_replace('/\r?\n(?not \t| )/', '', php.header)
    drupal_set_header(php.header)
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



def file_download():
  """
   Call plugins that implement hook_file_download() to find out if a file is
   accessible and what headers it should be transferred with + If a plugin
   returns -1 drupal_access_denied() will be returned + If one or more plugins
   returned headers the download will start with the returned headers + If no
   plugins respond drupal_not_found() will be returned.
  """
  # Merge remainder of arguments from php.GET['q'], into relative file path.
  args = func_get_args()
  filepath = php.implode('/', args)
  # Maintain compatibility with old ?file=paths saved in node bodies.
  if (php.isset(php.GET, 'file')):
    filepath =  php.GET['file']
  if (php.file_exists(file_create_path(filepath))):
    headers = plugin_invoke_all('file_download', filepath)
    if (php.in_array(-1, headers)):
      return drupal_access_denied()
    if (php.count(headers)):
      file_transfer(filepath, headers)
  return drupal_not_found()



def file_scan_directory(dir, mask, nomask = ['.', '..', 'CVS'], \
    callback = 0, recurse = True, key = 'filename', min_depth = 0, depth = 0):
  """
   Finds all files that match a given mask in a given directory.
   Directories and files beginning with a period are excluded; this
   prevents hidden files and directories (such as SVN working directories)
   from being scanned.
  
   @param dir
     The base directory for the scan, without trailing slash.
   @param mask
     The regular expression of the files to find.
   @param nomask
     An array of files/directories to ignore.
   @param callback
     The callback function to call for each match.
   @param recurse
     When True, the directory scan will recurse the entire tree
     starting at the provided directory.
   @param key
     The key to be used for the returned array of files + Possible
     values are "filename", for the path starting with dir,
     "basename", for the basename of the file, and "name" for the name
     of the file without an extension.
   @param min_depth
     Minimum depth of directories to return files from.
   @param depth
     Current depth of recursion + This parameter is only used
     internally and should not be passed.
  
   @return
     An associative array (keyed on the provided key) of objects with
     "path", "basename", and "name" members corresponding to the
     matching files.
  """
  key = (key if php.in_array(key, \
    ('filename', 'basename', 'name')) else 'filename')
  files = []
  if php.is_dir(dir):
    dir_files = php.scandir(dir)
    for file in dir_files:
      if (not php.in_array(file, nomask) and file[0] != '.'):
        if (php.is_dir("%s/%s" % (dir, file)) and recurse):
          # Give priority to files in this folder by
          # merging them in after any subdirectory files.
          files = php.array_merge(file_scan_directory("%s/%s" % (dir, file), \
            mask, nomask, callback, recurse, key, min_depth, depth + 1), files)
        elif (depth >= min_depth and ereg(mask, file)):
          # Always use this match over anything already
          # set in files with the same $key.
          filename = "%s/%s" % (dir, file)
          basename_ = php.basename(file)
          name = php.substr(basename_, 0, php.strrpos(basename_, '.'))
          files[key] = php.stdClass()
          files[key].filename = filename
          files[key].basename = basename_
          files[key].name = name
          if (callback):
            callback(filename)
  return files



def file_directory_temp():
  """
   Determine the default temporary directory.
  
   @return A string containing a temp directory.
  """
  temporary_directory = variable_get('file_directory_temp', None)
  if (is_None(temporary_directory)):
    directories = []
    # Has PHP been set with an upload_tmp_dir?
    if (ini_get('upload_tmp_dir')):
      directories.append( ini_get('upload_tmp_dir') )
    # Operating system specific dirs.
    if (php.substr(PHP_OS, 0, 3) == 'WIN'):
      directories.append( 'c:\\windows\\temp' )
      directories.append( 'c:\\winnt\\temp' )
      path_delimiter = '\\'
    else:
      directories.append( '/tmp' )
      path_delimiter = '/'
    for directory in directories:
      if (not temporary_directory and php.is_dir(directory)):
        temporary_directory = directory
    # if a directory has been found, use it,
    # otherwise default to 'files/tmp' or 'files\\tmp'
    temporary_directory = (temporary_directory if \
      (temporary_directory != None) else \
      (file_directory_path() +  path_delimiter + 'tmp'))
    variable_set('file_directory_temp', temporary_directory)
  return temporary_directory



def file_directory_path():
  """
   Determine the default 'files' directory.
  
   @return A string containing the path to Drupal's 'files' directory.
  """
  return variable_get('file_directory_path', conf_path() + '/files')


def file_upload_max_size():
  """
   Determine the maximum file upload size by querying the PHP settings.
  
   @return
     A file size limit in bytes based on the PHP
     upload_max_filesize and post_max_size
  """
  php.static(file_upload_max_size, 'max_size', -1)
  if (file_upload_max_size.max_size < 0):
    upload_max = parse_size(ini_get('upload_max_filesize'))
    post_max = parse_size(ini_get('post_max_size'))
    file_upload_max_size.max_size = (upload_max if \
      (upload_max < post_max) else post_max)
  return max_size


