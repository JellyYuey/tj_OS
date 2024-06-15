#include<iostream>
#include <windows.h>
#include <iomanip>
#include<ctime>
#include<random>
#include<string>
#define INSTRUCTION_COUNT 320//һ��ִ��320��ָ��
#define PAGE_NUM 4//�����һ����ҵ��ҳ��
#define INSTRUCTION_OF_PAGE 10//ÿһҳ��ָ������
using namespace std;
class Page {
public:
	int pageNumber;//ҳ�ţ�ȡֵΪ0��INSTRUCTION_COUNT-1
	int time;//��¼���뵽�ڴ��е�ʱ��,timeԽ��˵��Խ�����
	int dis;//��¼���뵱ǰִ��ָ��ľ��룬ÿһ��ִ�е�ǰҳ���ڵ�ָ��ʱ������
	Page(int pn=-1) :pageNumber(pn), time(0),dis(0){};
};
void input(int& option) 
{
	cout << "��ѡ���û��㷨" << endl;
	cout << "1.FIFO�㷨" << endl;
	cout << "2.LRU�㷨" << endl;
	while (1) {
		cout << "��ѡ��";
		cin >> option;
		if (cin.fail() || (cin.good() && option != 1 && option != 2)) {
			cout << "����ѡ��Ϸ������������롣" << endl;
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
	//��ȡһ������ʱ�����ҳ��
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
			return i;//��������ҳ��
	}
	return -1;
}
int main() 
{
	while (1) {
		int option;
		system("cls");
		input(option);//��������һ��ѡ��
		int (*algorithm)(Page*) = (option == 1 ? FIFO : LRU);//������ҳ����ȵĺ�����ָ��
		system("cls");
		srand(time(nullptr));

		int count = 0;//��¼ִ��ָ�������
		int pageFaults = 0;//ȱҳ����
		int m = rand() % INSTRUCTION_COUNT;//���������һ��ָ��ִ��
		Page pages[PAGE_NUM];//���ڼ�¼�ڴ����ڴ���ʹ�����


		while (count < INSTRUCTION_COUNT) {//һ��ִ��320��ָ��
			cout << "��" << right << setw(3) << count << "��ָ��  ";

			int page = m / INSTRUCTION_OF_PAGE;//�����ָ������ҳ��
			int memoryAddress = isInMemory(page, pages);//�鿴��ҳ�Ƿ����ڴ���

			for (int i = 0; i < PAGE_NUM; i++)//����ÿһ��ҳ�ľ��붼+1
				pages[i].dis++;

			string message;

			if (memoryAddress == -1) {//�����ҳ�����ڴ���
				++pageFaults;//ȱҳ����+1
				int targetPage = algorithm(pages);//��ȡ�������λ��
				pages[targetPage].pageNumber = page;
				pages[targetPage].time = 0;
				pages[targetPage].dis = 0;
				message = "ȱҳ��";
			}
			else {
				pages[memoryAddress].dis = 0;//�޸ľ���Ϊ0
				message = "�����ַ��" + to_string(memoryAddress) + "+" + to_string(m % INSTRUCTION_OF_PAGE);
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
			count++;//ָ���ִ�д���+1
			/*Sleep(1000);*/
		}

		cout << "ȱҳ�ʣ�" << ((double)pageFaults / INSTRUCTION_COUNT) << endl;
		char ch;
		while (1) {
			cout << "�Ƿ������(y/n)";
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
				cout << "����Ƿ���������ѡ��" << endl;
				cin.ignore(INT_MAX, '\n');
			}
		}
	}
	return 0;
}