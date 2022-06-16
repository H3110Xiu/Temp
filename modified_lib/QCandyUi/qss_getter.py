# const color string
WHITE = "#FFFFFF"
BLACK = "#000000"
RED = "#FF0000"
GREEN = "#00FF00"
BLUE = "#0000FF"
PURPLE = "#B23AEE"
WATCHET = "#1C86EE"
LIGHTGREEN = "#ECFEFE"
BLUEGREEN = "#33CCCC"
DEEPBLUEGREEN = "#015F5F"
DARKBLUEGREEN = "#28AAAA"
GRAY = "#999999"
LIGHTGRAY = "#CCCCCC"


def getFontQss(fontcolor):
    return "QObject{font-size:11pt;color:%s}" % (fontcolor)


def getPushButtonQss(normalColor, normalTextColor, hoverColor, hoverTextColor, pressedColor, pressedTextColor,
                     disableColor, disableTextColor):
    str1 = "QPushButton{padding:2px;min-height:15px;border-radius:5px;color:%s;background:%s;border:2px solid %s;}" % (
        normalTextColor, "#01060A", normalTextColor)
    str2 = "QPushButton:hover{color:%s;background:%s;}" % (hoverTextColor, hoverColor)
    str3 = "QPushButton:pressed{color:%s;background:%s;}" % (pressedTextColor, pressedColor)
    str4 = "QPushButton:disabled{color:%s;background:%s;}" % (disableTextColor, disableColor)
    return str1 + str2 + str3 + str4


def getLineeditQss(normalColor, focusColor):
    str1 = "QLineEdit{background-color:#19242A;border-style:none;padding:2px;border-radius:5px;" \
           "border:0px solid %s;selection-color:%s;selection-background-color:%s;}" % (
        normalColor, WHITE, focusColor)
    str2 = "QLineEdit:focus{border:2px solid %s;}" % (focusColor)
    str3 = "QLineEdit:disabled{color:%s;}" % (LIGHTGRAY)
    return str1 + str2 + str3


def getPlaineditQss(normalColor, focusColor):
    str1 = "QPlainTextEdit{border-style:none;padding:2px;border-radius:5px;border:2px solid %s;font-family:宋体;selection-color:%s;selection-background-color:%s}" % (
        normalColor, WHITE, focusColor)
    str2 = "QPlainTextEdit:focus{border:2px solid %s;}" % (focusColor)
    return str1 + str2


def getTextEditQss(normalColor, focusColor):
    str1 = "QTextEdit{background-color:#19242A;border-style:none;padding:2px;border-radius:5px;border:0px solid %s;selection-color:%s;selection-background-color:%s}" % (
        normalColor, WHITE, focusColor)
    return str1


def getTextBrowerQss(normalColor, focusColor):
    str1 = "QTextBrowser{border-style:none;padding:2px;border-radius:5px;border:2px solid %s;font-family:宋体;selection-color:%s;selection-background-color:%s}" % (
        normalColor, WHITE, focusColor)
    str2 = "QTextBrowser:focus{border:2px solid %s;}" % (focusColor)
    return str1 + str2


def getComboxQss(backgroundColor, normalColor, focusColor, arrowimageurl):
    str1 = "QComboBox{font-size:11pt;background:%s;padding:2px;border-radius:5px;border:0px solid %s;selection-background-color:%s;}" % (
        "#19242A", normalColor, focusColor)
    str2 = "QComboBox:focus{border:2px solid %s;}" % (focusColor)
    str3 = "QComboBox:on{border:2px solid %s}" % (focusColor)
    str8 = "QComboBox:on{border:2px solid %s;background:#19242A}" % (focusColor)
    str4 = "QComboBox:disabled{color:%s;}" % (LIGHTGRAY)
    str5 = "QComboBox::drop-down{border-style:solid;}"
    str6 = "QComboBox QAbstractItemView{border:2px solid %s;border-radius:5px;background:transparent;selection-background-color:%s;}" % (
        focusColor, focusColor)
    str7 = "QComboBox::down-arrow{image:url(%s)}" % (arrowimageurl)
    return str1 + str2 + str3 + str4 + str5 + str6 + str7 + str8


def getProgressBarQss(normalColor, chunkColor):
    barHeight = str(8)
    barRadius = str(8)
    str1 = "QProgressBar{min-height:22px;height:%spx;background:%s;border-radius:%spx;text-align:center;border:1px solid %s;}" % (
        barHeight, normalColor, barRadius, normalColor)
    str2 = "QProgressBar:chunk{border-radius:%spx;background-color:%s;width:10px;margin:1px}" % (barRadius, chunkColor)
    return str1 + str2


def getSliderQss(normalColor, grooveColor, handleColor):
    sliderHeight = str(8)
    sliderRadius = str(4)
    handleWidth = str(13)
    handleRadius = str(6)
    handleOffset = str(3)
    str1 = "QSlider::groove:horizontal,QSlider::add-page:horizontal{height:%spx;border-radius:%spx;background:%s;}" % (
        sliderHeight, sliderRadius, normalColor)
    str2 = "QSlider::sub-page:horizontal{height:%spx;border-radius:%spx;background:%s;}" % (
        sliderHeight, sliderRadius, grooveColor)
    str3 = "QSlider::handle:horizontal{width:%spx;margin-top:-%spx;margin-bottom:-%spx;border-radius:%spx;background:qradialgradient(spread:pad,cx:0.5,cy:0.5,radius:0.5,fx:0.5,fy:0.5,stop:0.6 #FFFFFF,stop:0.8 %s);}" % (
        handleWidth, handleOffset, handleOffset, handleRadius, handleColor)
    return str1 + str2 + str3


def getRadioButtonQss(normimageurl, downimageurl, normimageurlhover, downimageurlhover):
    str1 = "QRadioButton::indicator{width:15px;height:15px;}"
    str2 = "QRadioButton::indicator:unchecked{image: url(%s);}" % (normimageurl)
    str3 = "QRadioButton::indicator:checked{image: url(%s);}" % (downimageurl)
    str4 = "QRadioButton::indicator:checked:hover{image: url(%s);}" % (downimageurlhover)
    return str1 + str2 + str3 + str4


def getCheckBoxQss(normimageurl, checkimageurl, normimageurlhover, checkimageurlhover):
    str1 = "QCheckBox::indicator{width:15px;height:15px;}"
    str2 = "QCheckBox::indicator:unchecked{image: url(%s);}" % (normimageurl)
    str3 = "QCheckBox::indicator:checked{image: url(%s);}" % (checkimageurl)
    str4 = "QCheckBox::indicator:unchecked:hover{image: url(%s);}" % (normimageurlhover)
    str5 = "QCheckBox::indicator:checked:hover{image: url(%s);}" % (checkimageurlhover)
    return str1 + str2 + str3 + str4 + str5


def getTabWidgetQss(normalTabColor, normalTabTextColor, tabBorderColor):
    str1 = "QTabWidget{background:%s;}" % ("#03141C")
    str2 = "QTabWidget::tab-bar{left:5px}"
    str3 = "QTabBar::tab{color:%s; background:%s;width:80px;height:25px;border:2px solid %s;border-radius:2px}" % (
        "#E1D08F", normalTabColor, tabBorderColor)
    str4 = "QTabBar::tab:hover{color:%s; background:%s;}" % (normalTabColor, normalTabTextColor)
    str5 = "QTabBar::tab:selected{color:%s; background:%s;}" % (normalTabColor, normalTabTextColor)
    return str1 + str3 + str4 + str5


def getScrollbarQss(handlebarcolor):
    str1 = "QScrollBar{background:transparent;width:10px;padding-top:11px;padding-bottom:11px}"
    str2 = "QScrollBar::handle{background:%s;border-radius:5px;min-height:10px}" % (handlebarcolor)
    str3 = "QScrollBar::handle:pressed{background:%s}" % (GRAY)
    return str1 + str2 + str3
