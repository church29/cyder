function enableBatchUpdate() {
    //Remove batch update mode
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
        var $tr = $(tr);
        $tr.append('<th><input type="checkbox" name="interfaceCheck" /></th>');
    });
    $('#selectAll').change(function() {
        var $all = $(this).attr('checked');
        $('input[name=interfaceCheck]').each(function() {
            $(this).attr('checked', $all);
        });
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
