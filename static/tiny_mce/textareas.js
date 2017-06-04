tinyMCE.init({
    theme: "advanced",
    mode : "textareas",
    theme : "advanced",
    //content_css : "/appmedia/blog/style.css",
    theme_advanced_toolbar_location : "top",
    theme_advanced_toolbar_align : "left",
    theme_advanced_buttons1 : "fullscreen,separator,preview,separator,bold,italic,underline,strikethrough,separator,bullist,numlist,outdent,indent,separator,undo,redo,separator,link,unlink,anchor,separator,image,cleanup,help,separator,code",
    theme_advanced_buttons2 : "",
    theme_advanced_buttons3 : "",
    auto_cleanup_word : true,
    plugins : "style,advimage,advlink,advlist,inlinepopups,paste,fullscreen",
    plugin_insertdate_dateFormat : "%m/%d/%Y",
    plugin_insertdate_timeFormat : "%H:%M:%S",
    extended_valid_elements : "a[name|href|target=_blank|title|onclick],img[class|src|border=0|alt|title|hspace|vspace|width|height|align|onmouseover|onmouseout|name],hr[class|width|size|noshade],font[face|size|color|style],span[class|align|style]",
    fullscreen_settings : {
        theme_advanced_path_location : "top",
        theme_advanced_buttons1 : "bold,italic,|,forecolor,|,formatselect,|,bullist,numlist,|,link,unlink,|,fullscreen,|,code",
        theme_advanced_buttons2 : "code,paste,pastetext,pasteword,removeformat,|,backcolor,|,underline,justifyfull,sup,|,outdent,indent,|,hr,anchor,charmap,|,media,|,search,replace,|,fullscreen,|,undo,redo",
        theme_advanced_buttons3 : "visualaid"
    }
});
