$('#blah').hide();
$('#remove').hide();
$('#imgInp').on('keypress', function (e) {
    var keyCode = e.keyCode || e.which;
    if (keyCode === 13) {
        e.preventDefault();
        if (selectionRect) {
            if (formData.has('rect_start')) {
                formData.append('rect_end', JSON.stringify(selectionRect));
                submitRequest(formData);

                formData.delete('img')
                formData.delete('rect_start')
                formData.delete('rect_end')
                selectionRect = {}
            } else {
                formData.append('rect_start', JSON.stringify(selectionRect));
                formData.append('img', curImg);
            }
        }
        return false;
    }
});

var formData = new FormData();
var selectionRect = {};
var curImg;

function submitRequest() {
    (async () => {
        const rawResponse = await fetch(new URL('/submit', location), {
          method: 'POST',
          body: formData
        })
        .then(resp => resp.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            // the filename you want
            a.download = 'video.mp4';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            alert('your file has downloaded!'); // or you know, something with better UX...
        })
        .catch(() => alert('oh no!'));
      })();
}

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
                    selectionRect = (({ x1, x2, y1, y2 }) => ({ x1, x2, y1, y2 }))(area);
                    curImg = img.src;
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