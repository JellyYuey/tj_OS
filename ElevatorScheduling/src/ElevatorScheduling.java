import java.awt.*;
import java.awt.event.*;
import java.util.*;
import javax.swing.*;
import javax.swing.Timer;

public class ElevatorScheduling {
    public static void main(String[] args) {
        BrickFrame frame = new BrickFrame();
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.show();
    }
}

class BrickFrame extends JFrame {
    public BrickFrame() {
        setTitle("Lift--------Version  1.0");
        setSize(WIDTH, HEIGHT);

        BrickPanel myPanel = new BrickPanel();
        Container contentPane = getContentPane();
        contentPane.add(myPanel);
    }

    public static final int WIDTH = 600;
    public static final int HEIGHT = 600;
}

class BrickPanel extends JPanel {

    public BrickPanel() {
        setLayout(new BorderLayout());

        //初始化成员变量
        brick = new ArrayList(100);
        numberBrick = new ArrayList(100);
        controlBrick = new ArrayList(40);
        doorBrick=new ArrayList(10);
        panel = new JPanel();
        panel.setLayout(new GridLayout(22, 10));

        display = new TextField[5];

        for (int i = 0; i < 5; i++) {
            //初始化显示电梯楼层的GUI界面
            display[i] = new TextField("1");
            panel.add(display[i]);

            JButton button = new JButton();
            button.setBackground(Color.gray);
            panel.add(button);
        }

        for (int i = 0; i < 20; i++)
            for (int j = 0; j < 5; j++) {
                JButton button = new JButton();
                //初始化电梯通道
                panel.add(button);
                button.setBackground(Color.black);

                brick.add(button);

                //初始化电梯内部数字按键
                JButton buttonNumber = new JButton("" + (20 - i));
                buttonNumber.addActionListener(new NumberListener(j, 20 - i));
                panel.add(buttonNumber);
                buttonNumber.setBackground(Color.white);
                numberBrick.add(buttonNumber);
            }

        for (int i = 0; i < 5; i++) {
            //初始化电梯的开、关门按键
            JButton buttonOpen = new JButton("开");
            buttonOpen.addActionListener(new OpenListener(i));
            panel.add(buttonOpen);
            buttonOpen.setBackground(Color.lightGray);
            doorBrick.add(buttonOpen);

            JButton buttonClose = new JButton("关");
            buttonClose.addActionListener(new CloseListener(i));
            panel.add(buttonClose);
            buttonClose.setBackground(Color.red);
            doorBrick.add(buttonClose);
        }

        table = new int[20][5];

        for (int i = 0; i < 20; i++)
            for (int j = 0; j < 5; j++)
                table[i][j] = 0;

        add(panel, BorderLayout.CENTER);

        controlPanel = new JPanel();
        controlPanel.setLayout(new GridLayout(22, 3));

        for (int i = 0; i < 2; i++) {
            JButton button = new JButton();
            controlPanel.add(button);
            button.setBackground(Color.gray);
        }

        for (int i = 0; i < 20; i++) {
            //初始化电梯门口上、下行按键
            JButton buttonUp = new JButton("上");
            buttonUp.addActionListener(new UpListener(20 - i));
            buttonUp.setBackground(Color.lightGray);
            controlPanel.add(buttonUp);
            controlBrick.add(buttonUp);

            JButton buttonDown = new JButton("下");
            buttonDown.addActionListener(new DownListener(20 - i));
            buttonDown.setBackground(Color.lightGray);
            controlPanel.add(buttonDown);
            controlBrick.add(buttonDown);
        }

        for (int i = 0; i < 2; i++) {
            JButton button = new JButton();
            controlPanel.add(button);
            button.setBackground(Color.gray);
        }

        controlTable = new int[20][2];
        for (int i = 0; i < 20; i++)
            for (int j = 0; j < 2; j++)
                controlTable[i][j] = 0;

        add(controlPanel, BorderLayout.EAST);

        upSignalTable = new int[20];
        downSignalTable = new int[20];

        for (int i = 0; i < 20; i++) {
            upSignalTable[i] = 0;
            downSignalTable[i] = 0;
        }

        startGame();
    }

    //开始电梯调度并开启任务分配定时器。
    public void startGame() {
        lift = new LiftThread[5];
        for (int i = 0; i < 5; i++) {
            lift[i] = new LiftThread(i);
        }

        ActionListener timerlistener = new TaskTimerListener();
        timer = new Timer(800, timerlistener);
        timer.start();
    }

    //判断当前电梯内的数字键是否被按下，如有键被按下，则值为1，如果没有任何键被按下，则值为0。
    public boolean workState(int liftNumber) {
        for (int i = 0; i < 20; i++) {
            if (table[i][liftNumber] == 1)
                return true;
        }
        return false;
    }

    //重新刷新整个table，使每个button显示应该的颜色。
    public void drawBrick() {
        for (int i = 1; i <= 20; i++)
            for (int j = 1; j <= 5; j++) {
                ((JButton) brick.get((i - 1) * 5 + j - 1)).setBackground(
                        Color.black);
            }

        for (int i = 0; i < 5; i++) {
            ((JButton) brick.get((20 - lift[i].currentFloor) * 5 + i)).setBackground(
                    Color.blue);
        }
    }

    //将所有电梯内的数字键重新按当前状态显示颜色。
    public void drawNumberBrick() {
        for (int i = 0; i < 20; i++)
            for (int j = 0; j < 5; j++)
                if (table[i][j] == 1)
                    ((JButton) numberBrick.get(i * 5 + j)).setBackground(
                            Color.yellow);
                else
                    ((JButton) numberBrick.get(i * 5 + j)).setBackground(
                            Color.white);
    }

    //将所电梯口的上下键全部重新按当前状态显示颜色。
    public void drawControlBrick() {
        for (int i = 0; i < 20; i++)
            for (int j = 0; j < 2; j++)
                if (controlTable[i][j] == 1)
                    ((JButton) controlBrick.get(i * 2 + j)).setBackground(
                            Color.green);
                else
                    ((JButton) controlBrick.get(i * 2 + j)).setBackground(
                            Color.lightGray);
    }

    public void drawDoorBrick(){
        for(int i=0;i<5;i++){
            if(lift[i].door==0){//如果门的状态是开
                ((JButton) doorBrick.get(i*2)).setBackground(
                        Color.red);
                ((JButton) doorBrick.get(i*2+1)).setBackground(
                        Color.lightGray);
            }
            else{
                ((JButton) doorBrick.get(i*2)).setBackground(
                        Color.lightGray);
                ((JButton) doorBrick.get(i*2+1)).setBackground(
                        Color.red);
            }
        }
    }

    //********************************************实例字段****************************************************

    //存放电梯通道
    private ArrayList brick;
    //存放电梯按键
    private ArrayList numberBrick;
    //存放电梯门口上、下行按键
    private ArrayList controlBrick;
    //存放开、关门按键
    private ArrayList doorBrick;
    //电梯上方用于显示电梯当前运行楼层的GUI
    private TextField[] display;
    //记录电梯内部的数字按键任务，table[floor][liftNumber]=1表示编号为liftNumber的电梯的第20-floor楼按键有任务
    private int[][] table;
    //记录电梯门口上、下行按键的任务
    // controlTable[floor][0]=1表示第20-floor楼的上行按键被按下
    // controlTable[floor][1]=1表示第20-floor楼的下行按键被按下
    private int[][] controlTable;
    //计时器
    private Timer timer;

    private JPanel panel;
    private JPanel controlPanel;

    //存放电梯线程的数组
    private LiftThread[] lift;
    //记录电梯门口的上行任务，upSignalTable[floor]代表第floor+1楼的上行按键被按下
    private int[] upSignalTable;
    //记录电梯门口的下行任务，downSignalTable[floor]代表第floor+1楼的上行按键被按下
    private int[] downSignalTable;

    //电梯线程的监听器
    private class LiftTimeListener implements ActionListener {
        //电梯编号，用于和相应电梯绑定
        int liftNumber = -1;

        LiftTimeListener(int l) {
            liftNumber = l;
        }

        public void actionPerformed(ActionEvent event) {

            //如果电梯当前经过楼层有来自内部数字按键的任务，则该任务完成并刷新电梯按键
            if (table[20 - lift[liftNumber].currentFloor][liftNumber] == 1) {
                table[20 - lift[liftNumber].currentFloor][liftNumber] = 0;
                drawNumberBrick();
            }
            //读取电梯状态
            int status = lift[liftNumber].status;

            //若电梯运行方向和外部按键方向相反，则外部按键任务完成
            if (status != 0&& lift[liftNumber].currentFloor == lift[liftNumber].aim) {
                //电梯下行
                if (status == 2) {
                    //修改对应按键的值并刷新按键
                    controlTable[20 - lift[liftNumber].currentFloor][2 - status] = 0;
                    drawControlBrick();
                    //代表对应上行任务完成
                    upSignalTable[lift[liftNumber].currentFloor - 1] = 0;
                }
                //电梯上行
                if (status == 1) {
                    //修改对应按键的值并刷新按键
                    controlTable[20 - lift[liftNumber].currentFloor][2 - status] = 0;
                    drawControlBrick();
                    //代表对应下行任务完成
                    downSignalTable[lift[liftNumber].currentFloor - 1] = 0;
                }
            }

            //若电梯上行且当前楼层有外部按键的上行任务，则任务完成
            if (status == 1) {
                if (controlTable[20 - lift[liftNumber].currentFloor][0] == 1) {
                    controlTable[20 - lift[liftNumber].currentFloor][0] = 0;
                    drawControlBrick();
                    //代表对应上行任务完成
                    upSignalTable[lift[liftNumber].currentFloor - 1] = 0;
                }
            }

            //若电梯下行且当前楼层有外部按键的下行任务，则任务完成
            if (status == 2) {
                if (controlTable[20 - lift[liftNumber].currentFloor][1] == 1) {
                    controlTable[20 - lift[liftNumber].currentFloor][1] = 0;
                    drawControlBrick();
                    //代表对应下行任务完成
                    downSignalTable[lift[liftNumber].currentFloor - 1] = 0;
                }
            }

            //若电梯原来运行方向为上行，检查该电梯是否还需要继续向上，即检查该电梯当前楼层之上是否有数字按键任务没有完成
            if (status == 1) {
                int count = 0;
                for (int i = lift[liftNumber].currentFloor; i <=20; i++)
                    if (table[20 - i][liftNumber] == 1) {
                        count = 1;
                        break;
                    }
                //如果该电梯上方没有未完成的数字按键任务且外部的按键任务也完成
                if (count == 0
                        && lift[liftNumber].currentFloor >= lift[liftNumber].aim) {
                    lift[liftNumber].status = 0;//则电梯可以在原地保持不动
                    //刷新电梯按键为未按状态
                    for (int i = 1; i <=20; i++) {
                        table[20 - i][liftNumber] = 0;
                    }
                    drawNumberBrick();
                }
            }

            //若电梯原来运行方向为下行，检查该电梯是否还需要继续向下，即检查该电梯当前楼层之下是否有数字按键任务没有完成
            if (status == 2) {
                int count = 0;
                for (int i = lift[liftNumber].currentFloor; i >=1; i--)
                    if (table[20 - i][liftNumber] == 1) {
                        count = 1;
                        break;
                    }
                //如果该电梯下方没有未完成的数字按键任务且外部的按键任务也完成
                if (count == 0
                        && lift[liftNumber].currentFloor <= lift[liftNumber].aim) {
                    lift[liftNumber].status = 0;
                    //刷新电梯按键为未按状态
                    for (int i = 1; i <=20; i++) {
                        table[20 - i][liftNumber] = 0;
                    }
                    drawNumberBrick();
                }
            }

            //若电梯不为静止，则按方向继续运行
            status = lift[liftNumber].status;

            if (status== 1)
                lift[liftNumber].currentFloor++;
            if (status == 2)
                lift[liftNumber].currentFloor--;

            //刷新楼层GUI和电梯通道
            display[liftNumber].setText("" + lift[liftNumber].currentFloor);
            drawBrick();
        }
    }

    //任务分配监听器
    private class TaskTimerListener implements ActionListener {
        public void actionPerformed(ActionEvent event) {
            //检查每一层楼的上行按键是否被按下，若被按下则进行任务分配
            for (int floor = 1; floor <=20; floor++) {
                if (upSignalTable[floor - 1] == 1) {
                    int liftNumber = -1;//记录电梯编号
                    int distance = 20;//记录编号为liftNumber的电梯当前所在楼层与任务楼层floor的距离
                    int direction = 0;//记录电梯接受该任务后的运行状态
                    //上行任务可以分配给运行状态为四种类型之一的电梯：
                    //当前楼层在floor下方且向上运行
                    //在floor下方且静止
                    //在floor上方且静止
                    //当前楼层在floor上方且向下运行但电梯内部数字按键任务已经全部完成
                    for (int i = 0; i < 5; i++) {
                        //当前楼层在floor下方且向上运行
                        int status=lift[i].status;
                        int currentFloor=lift[i].currentFloor;
                        if (status == 1 && currentFloor <= floor) {
                            if ((floor - currentFloor) < distance) {
                                direction = 1;
                                liftNumber = i;
                                distance = floor - currentFloor;
                            }
                        }
                        //在floor下方且静止
                        if (status == 0 && currentFloor <= floor) {
                            if ((floor - currentFloor) < distance) {
                                direction = 1;
                                liftNumber = i;
                                distance = floor - currentFloor;
                            }
                        }
                        //在floor上方且静止
                        if (status == 0 && currentFloor >= floor) {
                            if ((currentFloor - floor) < distance) {
                                direction = 2;
                                liftNumber = i;
                                distance = currentFloor - floor;
                            }
                        }
                        //当前楼层在floor上方且向下运行但电梯内部数字按键任务已经全部完成
                        if (status == 2
                                && !workState(i)
                                && currentFloor >= floor) {
                            if ((currentFloor - floor) < distance) {
                                direction = 2;
                                liftNumber = i;
                                distance = currentFloor - floor;
                            }
                        }
                    }
                    //重置被选中电梯的目标楼层以及运行方向
                    if (liftNumber != -1) {
                        lift[liftNumber].aim = floor;
                        //因为电梯的运行状态可能由静止变为上行或下行
                        //必须保证电梯在运行时门的关闭的
                        lift[liftNumber].door=1;
                        drawDoorBrick();

                        lift[liftNumber].status = direction;
                    }
                }
            }

            //检查每一层楼的上行按键是否被按下，若被按下则进行任务分配
            for (int floor = 1; floor < 21; floor++) {
                if (downSignalTable[floor - 1] == 1) {
                    int liftNumber = -1;//记录电梯编号
                    int distance = 20;//记录编号为liftNumber的电梯当前所在楼层与任务楼层floor的距离
                    int direction = 0;//记录电梯接受该任务后的运行状态
                    //上行任务可以分配给运行状态为四种类型之一的电梯：
                    //当前楼层在floor上方且向下运行
                    //在floor上方且静止
                    //在floor下方且静止
                    //当前楼层在floor下方且向上运行但电梯内部数字按键任务已经全部完成
                    for (int i = 0; i < 5; i++) {
                        int status=lift[i].status;
                        int currentFloor=lift[i].currentFloor;
                        //当前楼层在floor上方且向下运行
                        if (status == 2 && currentFloor >= floor) {
                            if ((currentFloor - floor) < distance) {
                                direction = 2;
                                liftNumber = i;
                                distance = currentFloor - floor;
                            }
                        }
                        //在floor上方且静止
                        if (status == 0 && currentFloor >= floor) {
                            if ((currentFloor - floor) < distance) {
                                direction = 2;
                                liftNumber = i;
                                distance = currentFloor - floor;
                            }
                        }
                        //在floor下方且静止
                        if (status == 0 && currentFloor <= floor) {
                            if ((floor - currentFloor) < distance) {
                                direction = 1;
                                liftNumber = i;
                                distance = floor - currentFloor;
                            }
                        }
                        //当前楼层在floor下方且向上运行但电梯内部数字按键任务已经全部完成
                        if (status == 1
                                && !workState(i)
                                && currentFloor <= floor) {
                            if ((floor - currentFloor) < distance) {
                                direction = 1;
                                liftNumber = i;
                                distance = floor - currentFloor;
                            }
                        }
                    }
                    //重置被选中电梯的目标楼层以及运行方向
                    if (liftNumber != -1) {
                        lift[liftNumber].aim = floor;
                        //因为电梯的运行状态可能由静止变为上行或下行
                        //必须保证电梯在运行时门的关闭的
                        lift[liftNumber].door=1;
                        drawDoorBrick();

                        lift[liftNumber].status = direction;
                    }
                }
            }
        }
    }

    //上行按键监听器
    private class UpListener implements ActionListener {
        //上行按键所在楼层
        int floor = 1;

        UpListener(int f) {
            floor = f;
        }

        //按键被按下时的动作
        public void actionPerformed(ActionEvent e) {
            //修改对应的上行任务数组并刷新按键
            controlTable[20 - floor][0] = 1;
            drawControlBrick();

            upSignalTable[floor - 1] = 1;
        }
    }

    //下行按键监听器
    private class DownListener implements ActionListener {
        //下行按键所在楼层
        int floor = 1;

        DownListener(int f) {
            floor = f;
        }

        //按键被按下时的动作
        public void actionPerformed(ActionEvent e) {
            //修改对应的下行任务数组并刷新按键
            controlTable[20 - floor][1] = 1;
            drawControlBrick();

            downSignalTable[floor - 1] = 1;
        }
    }

    //数字按键监听器
    private class NumberListener implements ActionListener {
        int liftNumber = -1;//绑定电梯
        int number = 0;//数字编号

        NumberListener(int ln, int n) {
            liftNumber = ln;
            number = n;
        }
        //乡音该数字按键被按下时的动作
        public void actionPerformed(ActionEvent e) {
            //修改电梯的任务数组
            table[20 - number][liftNumber] = 1;

            //若电梯原来为静止，则改变电梯状态
            lift[liftNumber].aim = number;
            int n = lift[liftNumber].currentFloor;
            if (lift[liftNumber].status == 0) {
                //注意修改静止电梯的状态时必须确保门处于关闭状态
                lift[liftNumber].door=1;
                drawDoorBrick();
                if (number > n)
                    lift[liftNumber].status = 1;
                if (number < n)
                    lift[liftNumber].status = 2;
            }
            //刷新数字按键
            drawNumberBrick();
        }
    }
    //开门按键监听器
    private class OpenListener implements ActionListener {
        int liftNumber = -1;//绑定电梯

        OpenListener(int ln) {
            liftNumber = ln;
        }
        //按键被按下时的动作
        public void actionPerformed(ActionEvent e) {
            if(lift[liftNumber].status==0)//如果电梯的状态为静止则可以开门
                lift[liftNumber].door=0;//将门的状态改为关
            drawDoorBrick();//刷新按键
        }
    }
    //关门按键监听器
    private class CloseListener implements ActionListener {
        int liftNumber = -1;//绑定电梯

        CloseListener(int ln) {
            liftNumber = ln;
        }

        public void actionPerformed(ActionEvent e) {
            lift[liftNumber].door=1;//将门的状态改为关
            drawDoorBrick();//刷新按键
        }
    }
    //电梯线程。
    private class LiftThread extends Thread {
        public int liftNumber = -1;//电梯编号
        public int currentFloor = 1;//电梯当前所在楼层
        public int status = 0;//电梯当前状态，0为静止，1为上升，2为下降
        public int door=1;//门的状态，0为开，1为关
        int aim;//目标楼层

        public LiftThread(int n) {
            liftNumber = n;
            start();
        }

        public void run() {
            //绑定电梯线程
            ActionListener timelistener = new LiftTimeListener(liftNumber);
            timer = new Timer(800, timelistener);
            timer.start();
        }
    }
}

