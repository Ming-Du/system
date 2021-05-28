#include "widget.h"
#include "ui_widget.h"
#include<iostream>
#include<fstream>
#include <QDir>
#include<QString>
#include<QtCore/QFile>
#include<QProcess>
#include<QMessageBox>
using namespace std;
Widget::Widget(QWidget *parent) :
    QWidget(parent),
    ui(new Ui::Widget)
{
    ui->setupUi(this);
    terminal_start = nullptr;
    terminal_stop = nullptr;
    terminal_vehicle = nullptr;
    qvehicle = "";
    qcartype = "";
    qstarttype = "";
    carList();

    connect(ui->comboBox_carNum,SIGNAL(currentTextChanged(QString)),ui->lineEdit_carNum,SLOT(setText(QString)));
    connect(ui->pushButton_start,SIGNAL(clicked(bool)),this,SLOT(auto_start()));
    connect(ui->pushButton_off,SIGNAL(clicked(bool)),this,SLOT(auto_stop()));
    connect(ui->comboBox_carType,SIGNAL(currentTextChanged(QString)),ui->lineEdit_carType,SLOT(setText(QString)));
    connect(ui->comboBox_startType,SIGNAL(currentTextChanged(QString)),ui->lineEdit_startType,SLOT(setText(QString)));


}

Widget::~Widget()
{
    delete ui;
    if(terminal_start == nullptr)
    {
        delete terminal_start;

    }
    if(terminal_start == nullptr)
    {
        delete terminal_stop;

    }
}

void Widget::carList()
{
    QDir qdir;
    QStringList qstrlist;
    QString cupath = qdir.currentPath();
    cout <<"cupath:" << cupath.toStdString() << endl;
    QFile qfile(":/conf/vehicle.conf");
    if (qfile.exists(":/conf/vehicle.conf") )
    {
        cout <<"exitst" << endl;

    }
    if(!qfile.open(QIODevice::ReadOnly))
   // if(qfile.handle()==-1)
    {

        qfile.close();
        cout << "can not open qfile" << endl;
    }
    QString qstrline;
    char line[1024] = {0};
    ui->comboBox_carNum->clear();

    while(!qfile.atEnd())
    {
        qfile.readLine(line,1024);
        cout << line << endl;
        qstrlist << line;

    }

    ui->comboBox_carNum->addItems(qstrlist);

    qfile.close();
    
    
}
void Widget::auto_start()
{
    int ret = initAuto();
    if(ret == -1)
    {
        return;
    }
    if(terminal_start != nullptr)
    {
        delete terminal_start;
        terminal_start = nullptr;
    }
    cout << "in auto_start" << endl;
    terminal_start = new QProcess;
    QString commond = "bash";
    if(qstarttype == "autopilot")
    {
        commond += " /home/mogo/autopilot/share/launch/autopilot.sh";
    }else if(qstarttype=="catkin_ws"){
        commond += " /home/mogo/catkin_ws/src/system/launch/start_integration.sh";
    }
    else{
        //
    }

    if(qcartype=="byd")
    {
        commond += " byd";
    }else if(qcartype=="wey")
    {
        commond += " wey";

    }else if(qcartype=="jinlv")
    {
        commond += " jinlv";

    }
    else
    {
        //
    }
    cout << "commond:" << commond.toStdString() << endl;
    terminal_start->start(commond);
    QString abc = terminal_start->readAllStandardOutput();
    QString abcd = terminal_start->readAllStandardError();

    cout << abc.toStdString() << abcd.toStdString()<< endl;
   // terminal_start->waitForFinished(20000);
    cout << "strat end" << endl;
}
void Widget::auto_stop()
{
    if(terminal_stop != nullptr)
    {
        delete terminal_stop;
        terminal_stop = nullptr;
    }
    cout << "in auto_stop" << endl;
   // terminal_stop = new QProcess;
   // QString commond = "ls -l";
  //    QString commond = "rosnode kill -a";
    QString commond = "bash /home/mogo/catkin_ws/src/system/launch/shutdown.sh";
  //  connect(this->terminal_stop,SIGNAL(readyReadStandardOutput()),this,SLOT(readStop()));
   // terminal_stop->setReadChannel(QProcess::StandardOutput);
   // connect(this->terminal_stop,SIGNAL(readyReadStandardError()),this,SLOT(readStop()));
   // terminal_stop->setReadChannel(QProcess::StandardError);
   // terminal_stop->start(commond);
//    QString abc = terminal_stop->readAllStandardOutput();
  //  char stop_str[1024] = {0};

    //terminal_stop->readLine(stop_str,1024);
  //  cout << "stop_str:" << stop_str << endl;
  //  QString abcd = terminal_stop->readAllStandardError();

  //  cout << abc.toStdString() << abcd.toStdString()<< endl;
    char buf[1024] = {0};
            FILE *f_p = popen(commond.toStdString().c_str(),"r");
            while(fgets(buf,1024,f_p))
            {
                cout<<buf << endl;

            }
            pclose(f_p);

}
void Widget::setVehicle()
{
    qvehicle = ui->lineEdit_carNum->text();
    cout << "qvehicle:" << qvehicle.toStdString() << endl;
}
void Widget::setStartType()
{
    qstarttype = ui->lineEdit_startType->text();
    cout << "qstarttype:" << qstarttype.toStdString() << endl;
}
void Widget::setCarType()
{
    qcartype = ui->lineEdit_carType->text();
    cout << "qcartype:" << qcartype.toStdString() << endl;
}

void Widget::lnAutopiot()
{

}
void Widget::lnVehicle()
{
    if(terminal_vehicle != nullptr)
    {
        delete terminal_vehicle;
        terminal_vehicle = nullptr;
    }

    if(qstarttype == "catkin_ws")
    {
        cout << "ln catkin_ws" << endl;

        terminal_vehicle = new QProcess;
        QFile qfile("/homo/mogo/catkin_ws/src/system/config/vehicle");
       if(qfile.exists("/homo/mogo/catkin_ws/src/system/config/vehicle"))
        {
            QString rmcommond = "rm -rf /home/mogo/catkin_ws/src/system/config/vehicle";
            cout << "rmcommond:" << rmcommond.toStdString() << endl;

            terminal_vehicle->start(rmcommond);
            terminal_vehicle->waitForFinished(2000);
        }

        QString lncommond = "ln -s /home/mogo/catkin_ws/src/system/config/" + qvehicle + " /home/mogo/catkin_ws/src/system/config/vehicle";
        cout << "lncommond:" << lncommond.toStdString() << endl;
        terminal_vehicle->start(lncommond);
        terminal_vehicle->waitForFinished(2000);
    }
    if(qstarttype == "autopilot")
    {
        cout << "ln catkin_ws" << endl;
        QDir dir;
        if(!dir.exists("/home/mogo/autopilot"))
        {
            QMessageBox::critical(this,"error","没有autopilot,请先部署版本");
        }
        terminal_vehicle = new QProcess;
        QFile qfile("/homo/mogo/autopilot/share/config/vehicle");
        if(qfile.exists())
        {
            QString rmcommond = "rm -rf /homo/mogo/autopilot/share/config/vehicle";
            terminal_vehicle->start(rmcommond);
            terminal_vehicle->waitForFinished(2000);
        }

        QString lncommond = "ln -s /homo/mogo/autopilot/share/config/" + qvehicle + " /homo/mogo/autopilot/share/config/vehicle";
        terminal_vehicle->start(lncommond);
        terminal_vehicle->waitForFinished(2000);
    }
}
int Widget::initAuto()
{
    setVehicle();
    setStartType();
    setCarType();
    if(qvehicle=="")
    {
        QMessageBox::critical(this,"error","【车牌号】未输入");
        return -1;

    }
    if(qstarttype=="")
    {
        QMessageBox::critical(this,"error","【类型】未输入");
        return -1;

    }
    if(qcartype=="")
    {
        QMessageBox::critical(this,"error","【车辆类型】未输入");
        return -1;

    }

    lnVehicle();
    return 0;
}
void Widget::readStop()
{
    cout << "in readStop" <<  endl;
    QString abc = terminal_stop->readAllStandardOutput();

    QString abcd = terminal_stop->readAllStandardError();

    cout << abc.toStdString() << abcd.toStdString()<< endl;

}
