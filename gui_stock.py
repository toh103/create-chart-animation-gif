import PySimpleGUI as sg
import datetime
import stock as Stock


class WindowView:
    interval_tuple = tuple(
        '1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo'.split(','))
    text_area_size = (16, 1)
    input_area_size = (30, 1)
    button_area_size = (8, 1)
    default_font = ('Monaco', 16)
    current_datetime = datetime.datetime.now().strftime('%Y-%m-%d')
    text_default = {'font': default_font, 'size': text_area_size}
    input_default = {'font': default_font, 'size': input_area_size}
    button_default = {'font': default_font, 'size': button_area_size}

    def __init__(self):

        self.layout = [[sg.Text('StockCODE', **WindowView.text_default), sg.InputText(**WindowView.input_default, key='code')],
                       [sg.Text('From', **WindowView.text_default),
                        sg.InputText(WindowView.current_datetime, **WindowView.input_default, key='start_ymd')],
                       [sg.Text('To', **WindowView.text_default),
                        sg.InputText(WindowView.current_datetime, **WindowView.input_default, key='end_ymd')],
                       [sg.Text('---option----', **WindowView.text_default)],
                       [sg.Text('Interval', **WindowView.text_default), sg.InputCombo(
                           WindowView.interval_tuple, default_value="2m", font=WindowView.default_font, size=(5, 1), key='interval')],
                       [sg.Text('Show Graph', **WindowView.text_default),
                        sg.Radio('Enable', **WindowView.input_default, key='show_chart', group_id='mode')],
                       [sg.Text('Save Animation', **WindowView.text_default),
                        sg.Radio('Enable', **WindowView.input_default, key='save_anime', group_id='mode')],
                       [sg.Text('Save Directory', **WindowView.text_default),
                        sg.InputText('', **WindowView.input_default, key='save_dir')],
                       [sg.Text('File Name', **WindowView.text_default), sg.InputText(
                           '', **WindowView.input_default, key='file_name'), sg.Button('AUTO',  size=(6, 1), font=WindowView.default_font, key='-BUT_AUTO_FILE_NAME-')],
                       [sg.Exit('Exit', size=(6, 1), font=WindowView.default_font, button_color='coral'), sg.Button('DEFAULT',  size=(7, 1), font=WindowView.default_font, key='-BUT_DEFAULT-'), sg.Submit(
                           'Submit', size=(10, 1), font=WindowView.default_font, button_color='mediumaquamarine'), ]
                       ]
        self.window = sg.Window('Stock Animation Maker', self.layout,)

    def show_window(self):
        while True:
            event, values = self.window.read()
            if event is None:
                break
            elif event == 'Exit':
                break
            elif event == 'Submit':
                create_chart(values)
            elif event == '-BUT_DEFAULT-':
                print('BUT_A clicked')
                set_default(self.window)
            elif event == '-BUT_AUTO_FILE_NAME-':

                self.window['file_name'].update()
        self.window.close()


def set_default(window):
    current_datetime = datetime.datetime.now().strftime('%Y-%m-%d')
    default_code = '^NDX'
    default_interval = '2m'
    default_save_dir = 'anime'
    default_file_name = '{}_{}_{}.mp4'.format(
        default_code, current_datetime, default_interval)
    default_dict = {
        'code': default_code,
        'start_ymd': current_datetime,
        'end_ymd': current_datetime,
        'interval': default_interval,
        'show_chart': True,
        'save_anime': True,
        'save_dir': default_save_dir,
        'file_name': default_file_name
    }
    for key, value in default_dict.items():
        window[key].update(value)
    return


def create_chart(values):
    code = values['code']
    start_ymd = values['start_ymd']
    end_ymd = values['end_ymd']
    interval = values['interval']
    show_chart = values['show_chart']
    save_anime = values['save_anime']
    save_dir = values['save_dir']
    file_name = values['file_name']

    if start_ymd != end_ymd:
        stock = Stock.Stock_specific(
            code=code,
            start_ymd=start_ymd,
            end_ymd=end_ymd,
            interval=interval)
    else:
        stock = Stock.Stock_1d(code=code, period="1d", interval=interval)
    anime = Stock.StockAnimation(stock)

    anime.animate(show_chart=show_chart,
                  save_anime=save_anime,
                  save_dir=save_dir,
                  file_name=file_name)


def main():
    window = WindowView()
    window.show_window()


if __name__ == '__main__':
    main()
