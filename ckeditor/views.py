from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.utils.safestring import mark_safe

from . import utils
from .settings import JQUERY_OVERRIDE_VAL


pretty_json_encode = utils.LazyEncoder(indent=4).encode


@csrf_exempt
def upload(request):
    """
    Uploads a file and send back its URL to CKEditor.

    TODO:
        Validate uploads
    """
    # Get the uploaded file from request.
    upload = request.FILES['upload']

    # Open output file in which to store upload.
    upload_filename = utils.get_upload_filename(upload.name, request.user)
    out = open(upload_filename, 'wb+')

    # Iterate through chunks and write to destination.
    for chunk in upload.chunks():
        out.write(chunk)
    out.close()

    url = utils.create_thumbnail(upload_filename)

    # Respond with Javascript sending ckeditor upload url.
    return HttpResponse("""
    <script type='text/javascript'>
        window.parent.CKEDITOR.tools.callFunction(%s, '%s');
    </script>""" % (request.GET['CKEditorFuncNum'], url))


def browse(request):
    context = RequestContext(request, {
        'images': utils.get_image_browse_urls(request.user),
    })
    return render_to_response('browse.html', context)


def configs(request):
    configs = getattr(settings, 'CKEDITOR_CONFIGS', None)
    merged_configs = {}
    if configs is not None:
        for config_name, config in configs.iteritems():
            merged_configs[config_name] = utils.validate_config(config_name)

    return render_to_response('ckeditor/configs.js', {
        'merged_configs': pretty_json_encode(merged_configs),
        'jquery_override_val': utils.json_encode(JQUERY_OVERRIDE_VAL),
    }, mimetype="application/x-javascript")
