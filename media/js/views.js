$(document).ready( function() {
    var metadata = $('#view-metadata');
    var form = $('#obj-form form')[0];
    var domainsUrl = metadata.attr( 'data-domainsUrl' );

    // For inputs with id = 'id_fqdn' | 'id_target' | server, make smart names.
    $( document ).on( 'click', '#id_fqdn, #id_target, #id_server', function() {
        if ( domainsUrl ) {
            make_smart_name_get_domains(
                $('#id_fqdn, #id_target, #id_server'), true, domainsUrl );
        }
    });

    // displays the loading gif on ajax event
    $(document).ajaxStart( function() {
        $('#busy-spinner').stop().fadeIn( 160 );
    }).ajaxStop( function() {
        $('#busy-spinner').stop().fadeOut( 160 );
    });

    // sidebar animation logic
    $('.nav-item.parent').click( function( e ) {
        e.preventDefault();
        var parentsChild = ( '#' + this.id + '-children' );
        $('#dns-sidebar-children, #dhcp-sidebar-children, #core-sidebar-children')
            .not(parentsChild).slideUp( 'slow' );
        $(parentsChild).slideToggle( 'slow' );
    });

    $( document ).on( 'click', '.exit-message', function( e ) {
        slideUp_and_remove( $(this).parent() );
    });

    $( document ).on( 'focus', '#id_attribute', function() {
        $('#id_attribute').autocomplete({
            minLength: 1,
            source: function( request, response ) {
                $.ajax({
                    global: false,
                    url: '/eav/search',
                    dataType: 'json',
                    data: {
                        term: request.term,
                        attribute_type: $('#id_attribute_type').val()
                    },
                    success: response
                });
            },
            delay: 400,
            select: function( event, ui ) {
                attributeName = ui.item.label;
            }
        });
    });

    $( document ).on( 'change', '#id_attribute_type', function() {
        $('#id_attribute').val( '' );
    });

    $( document ).on( 'click', '.js-get-form', function( e ) {
        // Show update form on clicking update icon.
        e.preventDefault();
        get_update_form( this );
    });

    function get_update_form( btn ) {
        var kwargs;
        var formTitle;
        var buttonLabel;
        var getData;
        var buttonAttrs;
        var initData;
        slideUp( $('#obj-form') );
        if ( $(btn).hasClass( 'selected' ) ) {
            return false;
        }
        form.action = btn.href;
        buttonAttrs = 'btn c js-submit';
        kwargs = JSON.parse( $(btn).attr( 'data-kwargs' ) );
        if ( kwargs.pk ) {
            getData = {
                'obj_type': kwargs.obj_type,
                'pk': kwargs.pk
            };
        } else {
            if ( $(btn).attr( 'data-init' ) ) {
                initData = $(btn).attr( 'data-init' );
            }

            getData = {
                'data': initData,
                'obj_type': kwargs.obj_type,
                'related_pk': metadata.attr( 'data-objPk' ),
                'related_type': metadata.attr( 'data-objType' ),
            };
        }

        $(document).scrollTop(0);
        $.ajax({
            type: 'GET',
            url: kwargs.get_url,
            data: getData,
            global: false,
            dataType: 'json',
            success: function( data ) {
                metaData = $('<div id="form-metadata">')
                    .attr( 'objType', kwargs.obj_type )
                    .attr( 'style', 'display:none' );
                setTimeout( function() {
                    $('#hidden-inner-form')
                        .empty()
                        .append( data.form )
                        .append( metaData );
                    initForms();
                }, 150 );
                $('#form-title').html( data.form_title );
                $('.form-btns .btn').not('.cancel')
                    .text( data.submit_btn_label )
                    .attr( 'class', buttonAttrs );
                $('#obj-form').slideDown();
            }
        });
    };


    function av_form_submit_handler( data ) {
        var is_update = false;
        var id = data.row.postback_urls[0].match(/[1-9]+/g);
        var kwargs;
        if ( $('.attrs_table:hidden') ) {
            $('.attrs_table').slideDown();
            $('.attrs_title').slideDown();
        }
        jQuery.each( $('.attrs_table > tbody > tr'), function( i, row ) {
            kwargs = JSON.parse(
                $(row).find( '.table_delete' ).attr( 'data-kwargs') );
            if ( kwargs.pk == id ) {
                $(this).remove();
                is_update = true;

            }
        });
        insertTablefyRow( data.row, $('.attrs_table > tbody') );
        if ( is_update ) {
            $('#obj-form form').find( '.cancel' ).click();
        } else {
            $('#obj-form form').trigger( 'reset' );
            $('#id_attribute').focus();
        }
    }

    // Form submit handler, special logic for attributes
    $( document ).on( 'click', '.js-submit', function( e ) {
        e.preventDefault();
        var form = $('#obj-form form');
        var url = form[0].action;
        var fields = form.find( ':input' ).serializeArray();
        var csrfToken = $('#view-metadata').attr( 'data-csrfToken' );
        $.when( ajax_form_submit( url, fields, csrfToken ) ).done( function( data ) {
            // for av forms
            if ( url.indexOf( '_av' ) >= 0 ) {
                av_form_submit_handler( data );
            } else {
                location.reload();
            }
        });
    });

    $( document ).on( 'mousemove', 'thead th', function(e) {
        if( is_inner_border( this, e ) ) {
            $(this).css('cursor', 'pointer');
        } else {
            $(this).css('cursor', 'default');
        }
    });

    $( document ).on( 'mousedown', 'thead th', function(e) {
        $( document ).on( 'selectstart dragstart', '*', function(e) {
            e.preventDefault();
        });
        var xCoord = e.pageX;
        var sel = '.' + $(this).attr('class');
        var width = $(sel).width();
        var pos = $(this).offset();
        var isLeftSide = xCoord - pos.left < 5;
        if( !is_inner_border( this, e ) ) {
            return false;
        }
            $( document ).on( 'mousemove', '*', function(e) {
                var xDist = e.pageX - xCoord;
                if( isLeftSide ) {
                    var newWidth = width - xDist > 0 ? width - xDist: width;
                } else {
                    var newWidth = width + xDist > 0 ? width + xDist: width;
                }
                $(sel).width( newWidth );
            });
        $(document).mouseup(function(e) {
            $(this).unbind( 'mousemove dragstart mouseup selectstart' );
        });
    });

    function is_inner_border( column, e ) {
        var xCoord = e.pageX;
        var sel = '.' + $(column).attr('class');
        ////////////////////////////////
        var colPos = $(column).offset();
        var colWidth = $(sel).width();
        ////////////////////////////////
        var table = $(column).closest('table');
        var tablePos = $(table).offset();
        var tableWidth = $(table).width();
        ////////////////////////////////
        var isLeftSideOfTable = xCoord - tablePos.left < 10;
        var isRightSideOfTable = tablePos.left + tableWidth - xCoord < 10;
        var isLeftSideOfColumn = xCoord - colPos.left < 5;
        var isRightSideOfColumn = colPos.left + colWidth - xCoord < 5;
        ////////////////////////////////
        if (isLeftSideOfTable || isRightSideOfTable) {
            return false;
        }
        if (isLeftSideOfColumn || isRightSideOfColumn) {
            return true;
        }
        return false;
    }
});

