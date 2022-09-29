import tkinter as tk


def timer_func():
    canvas.create_line(100, 100, 200, 200)
    print('ok')
    app.after(100, timer_func)


if __name__ == '__main__':
    app = tk.Tk()
    app.title('Canvas Sample')
    app.geometry('800x450')
    canvas = tk.Canvas(app, width=800, height=450)
    canvas.place(x=0, y=0)
    timer_func()
    app.mainloop()