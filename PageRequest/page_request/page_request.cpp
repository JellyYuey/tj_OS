#include<iostream>
#include <windows.h>
#include <iomanip>
#include<ctime>
#include<random>
#include<string>
#define INSTRUCTION_COUNT 320//一共执行320条指令
#define PAGE_NUM 4//分配给一个作业的页数
#define INSTRUCTION_OF_PAGE 10//每一页的指令条数
using namespace std;
class Page {
public:
	int pageNumber;//页号，取值为0到INSTRUCTION_COUNT-1
	int time;//记录进入到内存中的时间,time越大说明越早进入
	int dis;//记录距离当前执行指令的距离，每一次执行当前页面内的指令时就置零
	Page(int pn=-1) :pageNumber(pn), time(0),dis(0){};
};
void input(int& option) 
{
	cout << "请选择置换算法" << endl;
	cout << "1.FIFO算法" << endl;
	cout << "2.LRU算法" << endl;
	while (1) {
		cout << "请选择：";
		cin >> option;
		if (cin.fail() || (cin.good() && option != 1 && option != 2)) {
			cout << "输入选项不合法，请重新输入。" << endl;
			cin.clear();
			cin.ignore(INT_MAX,'\n');
		}
		else
			break;
	}
}
void printMemory(Page* pages,string &message)
{
	cout << "Memory:";
	for (int i = 0; i < PAGE_NUM; i++) {
		if (pages[i].pageNumber != -1)
			cout << right << setw(2) << pages[i].pageNumber;
		else
			cout << right << setw(2) << " ";
		cout << " ";
	}
	cout << message << endl;
}
int FIFO(Page*pages)
{
	int res = 0;
	//获取一个进入时间最长的页号
	for (int i = 0; i < PAGE_NUM; i++) {
		if (pages[i].pageNumber == -1) {
			res = i;
			break;
		}
		else if (pages[i].time > pages[res].time)
			res = i;
	}
	return res;
}
int LRU(Page* pages)
{
	int res = 0;
	for (int i = 0; i < PAGE_NUM; i++) {
		if (pages[i].pageNumber == -1) {
			res = i;
			break;
		}
		else if (pages[i].dis > pages[res].dis)
			res = i;
	}
	return res;
}
int isInMemory(int page, Page* pages)
{
	for (int i = 0; i < PAGE_NUM; i++) {
		if (pages[i].pageNumber == page)
			return i;//返回物理页号
	}
	return -1;
}
int main() 
{
	while (1) {
		int option;
		system("cls");
		input(option);//首先输入一个选项
		int (*algorithm)(Page*) = (option == 1 ? FIFO : LRU);//用于做页面调度的函数的指针
		system("cls");
		srand(time(nullptr));

		int count = 0;//记录执行指令的条数
		int pageFaults = 0;//缺页次数
		int m = rand() % INSTRUCTION_COUNT;//先随机生成一个指令执行
		Page pages[PAGE_NUM];//用于记录内存中内存块的使用情况


		while (count < INSTRUCTION_COUNT) {//一共执行320条指令
			cout << "第" << right << setw(3) << count << "条指令  ";

			int page = m / INSTRUCTION_OF_PAGE;//计算该指令所在页号
			int memoryAddress = isInMemory(page, pages);//查看该页是否在内存中

			for (int i = 0; i < PAGE_NUM; i++)//先让每一个页的距离都+1
				pages[i].dis++;

			string message;

			if (memoryAddress == -1) {//如果该页不在内存中
				++pageFaults;//缺页次数+1
				int targetPage = algorithm(pages);//获取被放入的位置
				pages[targetPage].pageNumber = page;
				pages[targetPage].time = 0;
				pages[targetPage].dis = 0;
				message = "缺页！";
			}
			else {
				pages[memoryAddress].dis = 0;//修改距离为0
				message = "物理地址：" + to_string(memoryAddress) + "+" + to_string(m % INSTRUCTION_OF_PAGE);
			}

			printMemory(pages, message);

			switch (count % 4) {
			case 0:
				++m;
				break;
			case 1:
				m = rand() % m;
				break;
			case 2:
				++m;
				break;
			case 3:
				m = m + rand() % (INSTRUCTION_COUNT - m);
				break;
			}
			count++;//指令的执行次数+1
			/*Sleep(1000);*/
		}

		cout << "缺页率：" << ((double)pageFaults / INSTRUCTION_COUNT) << endl;
		char ch;
		while (1) {
			cout << "是否继续？(y/n)";
			cin >> ch;
			if (ch == 'y' || ch == 'Y') {
				cin.ignore(INT_MAX, '\n');
				break;
			}
			else if (ch == 'n' || ch == 'N') {
				cin.ignore(INT_MAX, '\n');
				return 0;
			}
			else {
				cout << "输入非法，请重新选择。" << endl;
				cin.ignore(INT_MAX, '\n');
			}
		}
	}
	return 0;
}