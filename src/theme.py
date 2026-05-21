from tkinter import ttk

PARCHMENT = "#f5e6c8"       
DARK_BROWN = "#5c3a1e"     
GOLD = "#c9a227"            
CREAM = "#fdf5e6"           
BORDER_BROWN = "#8b6914"   
MUTED_BROWN = "#a08060"     
RED_WAX = "#8b1a1a"    
DEEP_BROWN = "#3d2410"

HEADING = ("Georgia", 14, "bold")
SUBHEADING = ("Georgia", 11, "bold")
BODY = ("Georgia", 10)
SMALL = ("Georgia", 9)
TINY = ("Georgia", 8)


def apply_theme(root):

    root.configure(bg=PARCHMENT)
    style = ttk.Style()
    style.theme_use("default")
    style.configure("TFrame", background=PARCHMENT)
    style.configure("TLabel", background=PARCHMENT, foreground=DARK_BROWN, font=BODY)
    style.configure(
        "TLabelframe",
        background=PARCHMENT,
        bordercolor=BORDER_BROWN,
        relief="groove",
    )
    style.configure(
        "TLabelframe.Label",
        background=PARCHMENT,
        foreground=GOLD,
        font=SUBHEADING,
    )

    style.configure(
        "TButton",
        background=CREAM,
        foreground=DARK_BROWN,
        font=BODY,
        borderwidth=2,
        relief="raised",
        padding=(8, 4),
    )
   
    style.map(
        "TButton",
        background=[("active", GOLD)],
        foreground=[("active", DEEP_BROWN)],
    )

    style.configure(
        "TEntry",
        fieldbackground=CREAM,
        foreground=DARK_BROWN,
        font=BODY,
    )

    style.configure(
        "TCombobox",
        fieldbackground=CREAM,
        foreground=DARK_BROWN,
        font=BODY,
        selectbackground=GOLD,
        selectforeground=DEEP_BROWN,
    )

    style.configure(
        "TCheckbutton",
        background=PARCHMENT,
        foreground=DARK_BROWN,
        font=SMALL,
    )

    style.configure(
        "TProgressbar",
        troughcolor=BORDER_BROWN,
        background=GOLD,
        borderwidth=1,
    )

    style.configure(
        "Treeview",
        background=PARCHMENT,
        foreground=DARK_BROWN,
        fieldbackground=PARCHMENT,
        font=BODY,
        borderwidth=1,
        rowheight=24,
    )
   
    style.configure(
        "Treeview.Heading",
        background=DARK_BROWN,
        foreground=GOLD,
        font=("Georgia", 10, "bold"),
        borderwidth=1,
        relief="raised",
    )

    style.map(
        "Treeview.Heading",
        background=[("active", BORDER_BROWN)],
    )

    style.configure(
        "Treeview",
        background=PARCHMENT,
        foreground=DARK_BROWN,
        fieldbackground=PARCHMENT,
    )

    style.configure(
        "TScrollbar",
        background=CREAM,
        troughcolor=BORDER_BROWN,
        borderwidth=1,
        arrowcolor=DARK_BROWN,
    )