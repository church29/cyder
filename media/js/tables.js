function enableBatchUpdate() {
    //Remove editable grid mode
    if ($('#enable-eg').length) {
        $('#enable-eg').remove()
    };
    // Remove Action column.
    if ($('th:contains("Actions")')) {
        $('th:contains("Actions")').remove();
        $('td:last-child').remove();
    }

    // Remove Info column.
    if ($('th:contains("Info")')) {
        $('th:contains("Info")').remove();
        $('td:first-child').remove();
    }
    $('#egtable').find('td, th').each(function (i, td) {
        var $td = $(td);
        if ($td.children().length) {
            $td.text($td.children()[0].innerHTML);
        }
        $td.text($td.text().trim());
    });
    $('#egtable').find('thead').find('tr:last').append('<th>select <input type="checkbox" id="selectAll" /></th>');
    $('#egtable').find('tbody').find('tr').each(function (i, tr) {
        var $id = $(tr).attr('data-url').split('/')[3];
        $(tr).append('<td><input type="checkbox" id="' + $id + '" name="interfaceCheck" /></td>');
    });
    $('#createInterface').text('Update Interfaces');
    $('#createInterface').attr('href', '#');

    $('#createInterface').click(function () {
        $('#batch-form').slideToggle();
    });
    $('#batch-cancel').click(function () {
        $('#batch-form').slideToggle();
    });
    $('#selectAll').change(function() {
        var $all = $(this).attr('checked');
        $('input[name=interfaceCheck]').each(function() {
            $(this).attr('checked', $all);
        });
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

        interface_type = $('#title').text();
        form = $('#batch-hidden-inner-form');
        range_id = form.find('#id_range').val();
        range_type = form.find('input:radio[name=range_type]:checked').val();
        var postData = {
            interfaces: interfaces,
            interface_type: interface_type,
            range: range_id,
            range_type: range_type,
        }
        $.post("/dhcp/interface/batch_update/", postData, function(data) {
        if (data.success) {
            location.reload();
        };
        if (data.error) {
            if (form.find('#error').length) {
                form.find('#error').remove();
            };
            form.append('<p id="error"><font color="red">' + data.error + '</font></p>');
        };
        }, 'json');


    });



}


function enableEditableGrid() {
    var $eg = $('#eg');
    if (!$eg) {
        return;
    }

    //Remove batch update mode
    if ($('#enable-batch-update').length) {
        $('#enable-batch-update').remove()
    };

    // Remove Action column.
    if ($('th:contains("Actions")')) {
        $('th:contains("Actions")').remove();
        $('td:last-child').remove();
    }

    // Remove Info column.
    if ($('th:contains("Info")')) {
        $('th:contains("Info")').remove();
        $('td:first-child').remove();
    }

    // Strip links and paragraph tags, remove table cell markdown until
    // we do CellRenderers.
    $('#egtable').find('td, th').each(function (i, td) {
        var $td = $(td);
        if ($td.children().length) {
            $td.text($td.children()[0].innerHTML);
        }
        $td.text($td.text().trim());
    });

    editableGrid = new EditableGrid("My Editable Grid");
    editableGrid.loadJSONFromString($eg.attr('data-metadata'));
    editableGrid.modelChanged = function(rowIndex, columnIndex, oldValue, newValue, row) {
        /*
        Callback function on change. Send whatever was changed so the change
        can be validated and the object can be updated.
        */
        var postData = {};
        postData[editableGrid.getColumnName(columnIndex)] = newValue;

        $.post($(row).attr('data-url'), postData, function(resp) {
            if (resp && resp.error) {
                $(row).after($('<tr></tr>').html(resp.error[0]));
            }
        }, 'json');
    };
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
            $this = $(this);
            if ($this.attr('checked')) {
                enableBatchUpdate();
            } else {
                location.reload();
            }
        });
    }

});
