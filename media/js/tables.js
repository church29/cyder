function enableEditableGrid(allPostData) {
    var $eg = $('#eg');
    var csrfToken = $('#view-metadata').attr('data-csrfToken');
    if (!$eg) {
        return;
    }

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
        var data = {};
        postData[editableGrid.getColumnName(columnIndex)] = newValue;
        postData['csrfmiddlewaretoken'] = csrfToken;
        data['row'] = row;
        data['postData'] = postData;
        data['url'] = $(row).attr('data-url');
        allPostData.push(data);
    };
    editableGrid.attachToHTMLTable('egtable');
    editableGrid.renderGrid();
}


$(document).ready(function() {
    var allPostData = [];
    var $enableEg = $('#enable-eg');
    if ($enableEg.length) {
        $enableEg[0].reset();

        // Enable editable grid on checkbox.
        $enableEg.find('input').removeAttr('disabled').change(function() {
            $this = $(this);
            if ($this.attr('checked')) {
                enableEditableGrid(allPostData);
                $this.attr('disabled', true);
            }

            $('#enable-eg').remove();
            $('.spreadsheet-mode').show();
            $('#action-bar').find('a').each(function() {
                $(this).css('display', 'none')
            });
            $('#action-bar').append('<a id="eg_submit" class="btn" href="#">Submit</a>');
            $('#eg_submit').click( function() {
                jQuery.each(allPostData, function(i, data) {
                    $.post(data.url, data.postData, function(resp) {
                        if (resp && resp.error) {
                            $(data.row).after($('<tr></tr>').html(resp.error));
                        }
                    }, 'json');
                });
            });

        });
    }
});
