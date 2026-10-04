#include "mainwindow.h"
#include "ui_mainwindow.h"

#include <QPixmap>

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
    , ui(new Ui::MainWindow)
{
    ui->setupUi(this);

    connect(ui->pushButton, &QPushButton::clicked, this, [this]()
            {
                QPixmap image(":/images/kitty_boom.png");

                ui->label->setPixmap(image);
                ui->label->setScaledContents(true);
            });
}

MainWindow::~MainWindow()
{
    delete ui;
}
