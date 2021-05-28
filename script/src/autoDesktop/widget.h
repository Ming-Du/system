#ifndef WIDGET_H
#define WIDGET_H

#include <QWidget>
#include<QProcess>
namespace Ui {
class Widget;
}

class Widget : public QWidget
{
    Q_OBJECT

public:
    explicit Widget(QWidget *parent = 0);
    ~Widget();

private:
    void carList();
    void setVehicle();
    void setCarType();
    void setStartType();
    void lnVehicle();
    void lnAutopiot();
    int initAuto();

public slots:
    void auto_start();
    void auto_stop();
    void readStop();
    

private:
    Ui::Widget *ui;
    QProcess *terminal_start;
    QProcess *terminal_stop;
    QProcess *terminal_vehicle;

    QString qvehicle;
    QString qcartype;
    QString qstarttype;


};

#endif // WIDGET_H
