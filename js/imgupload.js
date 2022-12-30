$('#blah').hide();
$('#remove').hide();
$('#imgInp').on('keyup keypress', function (e) {
    var keyCode = e.keyCode || e.which;
    if (keyCode === 13) {
        e.preventDefault();
        $.ajax({
            url: '/submit',
            type: 'POST',
            processData: false,
            contentType: false,
            data: formData,
            complete: function (data, status, xhr) {
            },
            success: function(data, status, xhr) {
                if (!data.renderingInProgress) {
                    alert('Now select the final frame.');
                } else {
                    alert('Your video is queued for rendering. Please wait...')
                }
            },
            error: function(xhr, status) {
                alert('Something went wrong. ' + xhr.status);
            }
        });
        return false;
    }
});

// $('#blah').hover(
//     function() {
//         $(this).animate({ 'zoom': 1.2 }, 400);
//     },
//     function() {
//         $(this).animate({ 'zoom': 1 }, 400);
//     });

var formData = new FormData();

function readURL(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();

        reader.onload = function (e) {
            $('#blah').attr('src', e.target.result);
            $('head').append('<meta name="viewport" content="width=device-width, initial-scale=5"/>');
            $('#blah').imgAreaSelect({
                handles: true,
                aspectRatio: '9:16',
                onSelectEnd: function (img, area) {
                    formData = new FormData();
                    formData.append('img', img);
                    var selectionRect = [];
                    selectionRect.push((({ x1, x2, y1, y2 }) => ({ x1, x2, y1, y2 }))(area));
                    formData.append('selectionRect', JSON.stringify(selectionRect))
                }
            });
        }

        reader.readAsDataURL(input.files[0]);
    }
}

$("#imgInp").change(function () {
    if ($('#imgInp').val() != "") {

        $('#remove').show();
        $('#blah').show();
    }
    else { $('#remove').hide(); $('#blah').hide(); }
    readURL(this);
});


$('#remove').click(function () {
    $('#imgInp').val('');
    $(this).hide();
    $('#blah').hide();
    $('#blah').imgAreaSelect({remove:true});
    $('#blah').attr('src', 'http://upload.wikimedia.org/wikipedia/commons/thumb/4/40/No_pub.svg/150px-No_pub.svg.png');
});