$('#blah').hide();
$('#remove').hide();  
function readURL(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        
        reader.onload = function (e) {
            $('#blah').attr('src', e.target.result);
            $('#blah').imgAreaSelect({
                handles: true,
                onSelectEnd: function (img, area) {
                    var formData = new FormData();
                    formData.append('img', img);
                    var selectionRect = [];
                    selectionRect.push((({ x1, x2, y1, y2 }) => ({ x1, x2, y1, y2 }))(area));
                    formData.append('selectionRect', JSON.stringify( objArr ))
                    $.ajax({
                        url: '/submit',
                        type: 'POST',
                        processData: false,
                        contentType: false,
                        data: formData,
                            complete: function(data, status, xhr){
                                alert('status: ' + status + ', data: ' + data.responseData);
                            }
                    });
                }
            });
        }
        
        reader.readAsDataURL(input.files[0]);
    }
}
    
$("#imgInp").change(function(){
    if( $('#imgInp').val()!=""){
        
        $('#remove').show();
        $('#blah').show();
    }
    else{ $('#remove').hide();$('#blah').hide();}
    readURL(this);
});


$('#remove').click(function(){
    $('#imgInp').val('');
    $(this).hide();
    $('#blah').hide();
    $('#blah').attr('src','http://upload.wikimedia.org/wikipedia/commons/thumb/4/40/No_pub.svg/150px-No_pub.svg.png');
});