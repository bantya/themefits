 #!/usr/bin/python
# -*- coding: utf-8 -*-

import sublime, sublime_plugin
import codecs, json
import plistlib
import glob
from os import path, remove


class SidebarMatchColorScheme(sublime_plugin.EventListener):

    def on_activated_async(self, view):
        global cache
        global settings
        settings = sublime.load_settings('SyncedSidebarBg.sublime-settings')
        scheme_file = view.settings().get('color_scheme')

        # do nothing if it's a widget
        if view.settings().get('is_widget'):
            return

        # do nothing if the sheme file is not available or the same as before
        if not scheme_file or scheme_file == cache.get('color_scheme'):
            return

        plist_file = plistlib.readPlistFromBytes(sublime.load_resource(scheme_file).encode('raw_unicode_escape'))
        global_settings = [i["settings"] for i in plist_file["settings"] if i["settings"].get("lineHighlight")]
        color_settings = global_settings and global_settings[0]

        if not color_settings:
            return

        bg = color_settings.get("background", '#FFFFFF')
        fg = color_settings.get("foreground", '#000000')
        bgc = bg.lstrip('#')
        cache = {"bg": bg, "fg": fg, "color_scheme": scheme_file}

        # -- COLOR ------------------------------

        _NUMERALS = '0123456789abcdefABCDEF'
        _HEXDEC = {v: int(v, 16) for v in (x + y for x in _NUMERALS for y in _NUMERALS)}

        def rgb(triplet):
            return _HEXDEC[triplet[0:2]], _HEXDEC[triplet[2:4]], _HEXDEC[triplet[4:6]]

        def is_light(triplet):
            r, g, b = _HEXDEC[triplet[0:2]], _HEXDEC[triplet[2:4]], _HEXDEC[triplet[4:6]]
            yiq = ((r * 299) + (g * 587) + (b * 114)) / 1000
            return yiq >= 128

        def color_variant(hex_color, brightness_offset=1):
            """ takes a color like #87c95f and produces a lighter or darker variant """
            if len(hex_color) == 9:
                print("=> Passed %s into color_variant()" % hex_color)
                hex_color = hex_color[0:-2]
                print("=> Reformatted as %s " % hex_color)
            if len(hex_color) != 7:
                raise Exception("Passed %s into color_variant(), needs to be in #87c95f format." % hex_color)
            rgb_hex = [hex_color[x:x + 2] for x in [1, 3, 5]]
            new_rgb_int = [int(hex_value, 16) + brightness_offset for hex_value in rgb_hex]
            new_rgb_int = [min([255, max([0, i])]) for i in new_rgb_int]  # make sure new values are between 0 and 255
            return "#%02x%02x%02x" % tuple(new_rgb_int)

        # --------------------------------------

        def label_color(triplet):
            if is_light(triplet):
                return settings.get('label_color_light')
            else:
                return settings.get('label_color_dark')

        def side_bar_sep_line(bg, brightness_change=settings.get('side_bar_sep_line_brightness_change')):
            global settings
            if is_light(bg.lstrip('#')):
                return rgb(color_variant(bg, -1 * brightness_change).lstrip('#'))
            else:
                return rgb(color_variant(bg, brightness_change).lstrip('#'))

        def bg_variat(bg):
            global settings
            if settings.get('sidebar_bg_brightness_change') == 0:
                return rgb(bgc)
            else:
                return rgb(color_variant(bg, settings.get('sidebar_bg_brightness_change')).lstrip('#'))

        template = [
            { 
                "class": "tool_tip_control",
                "layer0.tint": bg_variat(bg)
            },
            {
                "class": "tool_tip_label_control",
                "color": side_bar_sep_line(bg, 160)
            },
            {
                "class": "panel_close_button",
                "layer0.tint": side_bar_sep_line(bg, 120)
            },
            {
                "class": "close_button",
                "layer0.tint": side_bar_sep_line(bg, 120)
            },
            {
                "class": "tab_close_button",
                "layer0.tint": side_bar_sep_line(bg, 120)
            },
            {
                "class": "tab_close_button",
                "parents": [{"class": "tab_control","attributes": ["dirty","hover"]}],
                "layer0.tint": side_bar_sep_line(bg, 160)
            },
            {
        		"class": "show_tabs_dropdown_button",
        		"layer0.tint": side_bar_sep_line(bg,200)
    		},
    		{
        		"class": "show_tabs_dropdown_button",
        		"attributes": ["hover"],
        		"layer0.tint": side_bar_sep_line(bg,240)
    		},
            {
                "class": "status_bar",
                "layer0.tint": bg_variat(bg),
                "layer0.opacity": 1
            },
            {
        		"class": "overlay_control",
        		"layer0.tint": bg_variat(bg)
    		},	
    		{
        		"class": "popup_control",
        		"layer0.tint": bg_variat(bg)
    		},
            {
            	"class": "mini_quick_panel_row",
        		"layer0.tint": bg_variat(bg)
        	},
        	{
            	"class": "auto_complete",
        		"layer0.tint": bg_variat(bg)
        	},
    		{
        		"class": "auto_complete_label",
        		"fg": side_bar_sep_line(bg, 110), 
        		"match_fg": side_bar_sep_line(bg, 160), 
        		"selected_fg": side_bar_sep_line(bg, 150), 
        		"selected_match_fg": side_bar_sep_line(bg, 255)
    		},
        	{
        		"class": "quick_panel_label",
        		"fg": side_bar_sep_line(bg, 120), 
        		"match_fg": side_bar_sep_line(bg, 180), 
        		"selected_fg": side_bar_sep_line(bg, 200), 
        		"selected_match_fg": side_bar_sep_line(bg, 255)
    		}, 
    		{ 
        		"class": "quick_panel_path_label",
        		"fg": side_bar_sep_line(bg, 90), 
        		"match_fg": side_bar_sep_line(bg, 200), 
        		"selected_fg": side_bar_sep_line(bg, 120), 
        		"selected_match_fg": side_bar_sep_line(bg, 255)
    		}, 
            {
        		"class": "label_control",
        		"color": side_bar_sep_line(bg, 140)
    		},
            {
            	"class": "panel_control",
                "layer0.tint": bg_variat(bg),
            },            
            {
                "class": "scroll_bar_control",
                "layer0.tint": bg_variat(bg),
            },
            {
                "class": "tab_control", "attributes": ["selected"],
                "layer2.tint": side_bar_sep_line(bg, 255)
            },

            {
                "class": "disclosure_button_control",
                "layer0.tint": side_bar_sep_line(bg),
                "layer1.tint": side_bar_sep_line(bg)
            },
            {
                "class": "tree_row",
                "layer0.tint": side_bar_sep_line(bg, 50)
            },
            {
                "class": "tree_row",
                "attributes": ["selected"],
                "layer0.tint": bg_variat(bg)
            },
            {
                "class": "sidebar_tree",
                "layer0.tint": bg_variat(bg),
                "layer0.opacity": 1,
                "dark_content": not is_light(bgc)
            },
            {
                "class": "sidebar_label",
                "color": label_color(bgc),
            },
            {
        		"class": "sidebar_label",
        		"parents": [{"class": "tree_row"}],
        		"color": side_bar_sep_line(bg, 120)
    		},
    		{
        		"class": "sidebar_label",
        		"parents": [{"class": "tree_row", "attributes": ["selected"]}],
        		"color": side_bar_sep_line(bg, 180)
    		},
            {
                "class": "sidebar_heading",
                "color": side_bar_sep_line(bg, 120),
            },

            {
                "class": "icon_folder",
                "layer0.tint": side_bar_sep_line(bg, 120)
            },
            {
                "class": "icon_file_type",
                "layer0.tint": side_bar_sep_line(bg, 120)
            },
            {
                "class": "icon_folder_loading",
                "layer0.tint": side_bar_sep_line(bg, 250)
            },
            {
                "class": "icon_folder_dup",
                "layer0.tint": side_bar_sep_line(bg, 250)
            },
        ]

        json_str = json.dumps(template, sort_keys=True, indent=4, separators=(',', ': ')).encode('raw_unicode_escape')
        new_theme_file_path = sublime.packages_path() + "/User/" + view.settings().get('theme')
        with codecs.open(new_theme_file_path, 'w', 'utf-8') as f:
            f.write(json_str.decode())


def plugin_loaded():
    global cache
    global settings
    cache = {}
    settings = sublime.load_settings('SyncedSidebarBg.sublime-settings')


def plugin_unloaded():
    artifacts = path.join(sublime.packages_path(), "User", "*.sublime-theme")
    for f in glob.glob(artifacts):
        remove(f)