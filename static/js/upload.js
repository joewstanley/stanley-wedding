var MAX_LENGTH = 40;

var DEFAULT_WIDTH;
var DEFAULT_HEIGHT;

$(document).ready(function() {
    DEFAULT_WIDTH = parseInt($('.preview-panel').css('width'), 10);
    DEFAULT_HEIGHT = parseInt($('.preview-panel').css('height'), 10);

    if (getParameterByName('success') === 'True') {
        showSuccess();
    }

    $('#camera-upload').change(function(event) {
        $('#camera-radio').prop('checked', true);
        removeAlert('image-error');
        removeAlert('upload-success');
        drawUpload(event);
    });
    $('#file-upload').change(function(event) {
        $('#file-radio').prop('checked', true);
        removeAlert('image-error');
        removeAlert('upload-success');
        drawUpload(event);
    });

    $('#caption').on('keyup', function(event) {
        var str = $(this).val();
        var length = str.length;

        if (length > MAX_LENGTH) {
        $(this).val(str.substring(0, MAX_LENGTH));
            length = MAX_LENGTH;
        }

        $('.char-count').text(length + '/' + MAX_LENGTH);
    });
});

function getParameterByName(name) {
    var match = RegExp('[?&]' + name + '=([^&]*)').exec(window.location.search);
    return match && decodeURIComponent(match[1].replace(/\+/g, ' '));
}

function drawUpload(event) {
    var loadingImage = loadImage(
        event.target.files[0],
        function(image) {
            image.className = 'preview-canvas';
            $('.preview-panel').css('width', image.width);
            $('.preview-panel').css('height', image.height);

            if ($('.preview-image').length) {
                $('.preview-image').replaceWith(image);
            } else {
                $('.preview-canvas').replaceWith(image);
            }
        },
        {
            maxWidth:       DEFAULT_WIDTH,
            maxHeight:      DEFAULT_HEIGHT,
            contain:        true,
            orientation:    true
        }
    );
    var metadata = loadImage.parseMetaData(
        event.target.files[0],
        function(data) {
            if (data.exif != undefined) {
                var orientation = data.exif.get('Orientation');
                if (orientation != undefined) {
                    $('#orientation').val(orientation);
                }
            }
        }
    );
}

function validate() {
    var cameraUpload = $('#camera-upload').val();
    var fileUpload = $('#file-upload').val();
    if (!$('#camera-radio').prop('checked') && !$('#file-radio').prop('checked')) {
        showError('image-error', 'A photo must be uploaded for submission.');
        return false;
    }
    return true;
}

function showError(id, message) {
    var errorMessage = '<strong>Error!</strong> ' + message;
    $('#' + id).text(errorMessage);
    $('#' + id).removeClass('hidden').addClass('show');
}

function showSuccess() {
    $('#upload-success').removeClass('hidden').addClass('show');
}

function removeAlert(id) {
    $('#' + id).removeClass('show').addClass('hidden');
}