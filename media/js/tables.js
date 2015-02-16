function cleanTables() {
    // Remove Action column.
    if ( $('th:contains("Actions")') ) {
        $('th:contains("Actions")').remove();
        $('td:last-child').remove();
    }

    // Remove Info column.
    if ( $('th:contains("Info")') ) {
        $('th:contains("Info")').remove();
        $('td:first-child').remove();
    }

    // Strip links and paragraph tags, remove table cell markdown until
    // we do CellRenderers.
    $('#egtable').find( 'td, th' ).each( function ( i, td ) {
        var $td = $(td);
        if ( $td.children().length ) {
            $td.text( $td.children()[0].innerHTML );
        }
        $td.text( $td.text().trim() );
    });
}


function removeEditableGrid() {
    if ( $('#enable-eg').length ) {
        $('#enable-eg').remove();
    }
}


function removeBatchUpdate() {
    if ($('#enable-batch-update').length) {
        $('#enable-batch-update').remove();
    }
}


function appendSelectAllCheckBox() {
    $('#egtable').find( 'thead' ).find( 'tr:last' )
        .append( '<th>select <input type="checkbox" id="selectAll" /></th>' );
}


function appendCheckBoxesToRows() {
    $('#egtable').find( 'tbody' ).find( 'tr' ).each( function ( i, tr ) {
        var $id = $(tr).attr('data-url').split('/')[3];
        var $td = $('<td>').append( $('<input>')
            .attr( 'type', 'checkbox' )
            .attr( 'name', 'interfaceCheck' )
            .attr( 'class', 'batch-update-checkbox' )
            .attr( 'id', $id ) );
        $(tr).append($td);
    });
}

function addBatchUpdateExit() {
    var a = $('<a>')
        .attr( 'href', window.location.href )
        .text( 'Exit batch update mode' );
    $('.batch-update').append( a );

}


function enableBatchUpdate() {
    var csrfToken = $('#view-metadata').attr( 'data-csrfToken' );
    cleanTables();
    removeEditableGrid();
    removeBatchUpdate();
    addBatchUpdateExit();
    appendSelectAllCheckBox();
    appendCheckBoxesToRows();
    $('#system_create').remove();
    $('#batch_update_btn').css({'display': 'block'});

    $('#batch_update_btn, #batch-cancel').click(function (e) {
        $('#batch-form').slideToggle();
    });

    $('#selectAll').change( function() {
        var all = $(this).attr( 'checked' ) == "checked" ? true : false;
        $('input[name=interfaceCheck]').each( function() {
            $(this).attr( 'checked', all );
        });
    });

    $('input:radio[name=range_type]').live('change', function() {
        var postData = {
            csrfmiddlewaretoken: csrfToken,
            range_type: $(this).val(),
        };
        var url = "/dhcp/interface/batch_update_get_ranges/";
        $.post( url , postData, function( data ) {
            if (data.ranges) {
                form = $('#batch-hidden-inner-form');
                form.find('#id_range').empty();
                $.each(data.ranges, function() {
                    form.find('#id_range').append(
                        $('<option />').val(this[0]).text(this[1]));
                });
            } else {
                return false;
            }
        }, 'json');
    });

    $('#batch-submit').click(function (e) {
        e.preventDefault();
        var interfaces = "";
        $('input[name=interfaceCheck]').each(function (i, tr) {
            if ($(this).attr('checked')) {
                interfaces += this.id + ',';
            }
        });
        interfaces = interfaces.slice(0,-1);

        interface_type = $('#title').text().replace(
            ' Interfaces', 'interface').toLowerCase().trim();
        form = $('#batch-hidden-inner-form');
        range_id = form.find('#id_range').val();
        range_type = form.find('input:radio[name=range_type]:checked').val();
        site_id = form.find('#id_site').val();
        var postData = {
            interfaces: interfaces,
            interface_type: interface_type,
            range: range_id,
            range_type: range_type,
            csrfmiddlewaretoken: csrfToken,
            site: site_id,
        };
        $.ajax({
            type: 'POST',
            url: '/dhcp/interface/batch_update/',
            data: postData,
            dataType: 'json',
            beforesend: function() {
                $('.error').remove();
            },
        }).done( function( data ) {
            if (data.success) {
                location.reload();
            }
            if (data.error) {
                form.append('<p class="error">' + data.error + '</font></p>');
            }
        });
    });
}




/*
Callback function on change. Send whatever was changed so the change
can be validated and the object can be updated.
*/
function editableGridCallback(rowIndex, columnIndex, oldValue, newValue, row) {
    var postData = {};
    var csrfToken = $('#view-metadata').attr('data-csrfToken');
    postData[editableGrid.getColumnName(columnIndex)] = newValue;
    postData.csrfmiddlewaretoken = csrfToken;
    $.post($(row).attr('data-url'), postData, function(resp) {
        if (resp && resp.error) {
            $(row).after($('<tr></tr>').html(resp.error[0]));
        }
    }, 'json');
}


function enableEditableGrid() {
    var $eg = $('#eg');
    if (!$eg) {
        return;
    }

    cleanTables();
    removeBatchUpdate();
    editableGrid = new EditableGrid("My Editable Grid");
    editableGrid.loadJSONFromString($eg.attr('data-metadata'));
    editableGrid.modelChanged = editableGridCallback;
    editableGrid.attachToHTMLTable('egtable');
    editableGrid.renderGrid();
}


$(document).ready(function() {
    var $enableEg = $('#enable-eg');
    var $enableBatch = $('#enable-batch-update');
    if ($enableEg.length) {
        $enableEg[0].reset();

        // Enable editable grid on checkbox.
        $enableEg.find('input').removeAttr('disabled').change(function() {
            $this = $(this);
            if ($this.attr('checked')) {
                enableEditableGrid();
                $this.attr('disabled', true);
            }

            $('#enable-eg').remove();
            $('.spreadsheet-mode').show();
        });
    }
    if ($enableBatch.length) {
        $enableBatch[0].reset();
        $enableBatch.find('input').removeAttr('disabled').change(function() {
            if ($(this).attr('checked')) {
                enableBatchUpdate();
            } else {
                location.reload();
            }
        });
    }

});
