function enableEditableGrid(allPostData) {
    var $eg = $('#eg');
    var csrfToken = $('#view-metadata').attr('data-csrfToken');
    if (!$eg) {
        return;
    }

    // Remove Action column.
    if ($('.actions_column')) {
        $('.actions_column').remove();
    }

    // Remove Info column.
    if ($('.info_column')) {
        $('.info_column').remove();
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
        data['oldValue'] = oldValue;
        data['newValue'] = newValue;
        allPostData[rowIndex + '-' + columnIndex] = data;
    };
    editableGrid.attachToHTMLTable('egtable');
    editableGrid.renderGrid();
}


$(document).ready(function() {
    $.ajaxSetup({async:false});
    var allPostData = {};
    var $enableEg = $('#enable-eg');
    if ($enableEg.length) {
        $enableEg[0].reset();

        $('.exit-spreadsheet').click( function(e) {
            e.preventDefault();
            if (confirm('Are you sure you want to exit spreadsheet mode? ' +
                    'Your changes will not be submitted')) {
                location.reload();
           };
        });

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
                var confirm_str = "Are you sure you want to make the following changes?\n";
                jQuery.each(allPostData, function(i, data) {
                    confirm_str += data.oldValue + " -> " + data.newValue + "\n";
                });
                if (confirm(confirm_str)) {
                    $('.errors').each(function() {
                        $(this).remove();
                    });
                    var successIndex = [];
                    var success = true;
                    jQuery.each(allPostData, function(key, data) {
                        $.post(data.url, data.postData, function(resp) {
                            if (resp && resp.error) {
                                jQuery.each(resp.error, function(field, error) {
                                    if (field == '__all__') {
                                        $(data.row).after(
                                            '<tr class="errors"><td><font '
                                            + 'color="red">' + error +
                                            '</font></td></tr>');
                                    } else {
                                        field = $(data.row).find(
                                            '.' + field + '_column');
                                        field.append(
                                            '<font class="errors" color="red"> '
                                            + error + '</font>');
                                    };
                                });
                                success = false;
                            } else {
                                successIndex.push(key);
                            };
                        }, 'json');
                    });
                    if (success) {
                        location.reload();
                    } else {
                        jQuery.each(successIndex, function(index, key) {
                            delete allPostData[key];
                        });
                    };
                };
            });
        });
    }
});
