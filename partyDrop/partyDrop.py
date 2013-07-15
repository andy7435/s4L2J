from com.l2jserver.gameserver.model.quest.jython import QuestJython as JQuest
from com.l2jserver.gameserver.util import Util 

class Quest(JQuest):
	qID = -1 #�}�� ID, �ۭq�}�� �i�� -1
	qn = "partyDrop" #�}���W��, ���୫�дN�i�H
	qDesc = "custom" #�}������ / �M��}���� HTM ��m�ɥ�

	MOBSID = [22947,22948,22950,22956, 22957,23161]
	REWARD = [#[���~ID, �̤�, �̦h, ���v%]
	[57,1,100,50]
	,[57,2000,3000,99]
	]
	isSendMessage = False
	#isSendMessage = True

	def __init__(self, id = qID, name = qn, descr = qDesc):
		self.qID, self.qn, self.qDesc = id, name, descr #�]�w qid, qn �� qdesc (�p�G�b�}���̤U�H  Quest(-1, "abc", "custom") ����I�s)
		JQuest.__init__(self, id, name, descr) #�I�s��
		for id in self.MOBSID:
			self.addKillId(id) #�[�J ���@�өǪ��� ID �Q���|�I�s �o�̪� onKill
		print "%s loaded" % self.qn #��l�Ƨ��� GS ��ܰT��
		
	def sendMessage(self, player, message):
		if self.isSendMessage:
			player.sendMessage(message) #�V���a�o�X�T��
			
	def getIP(self, player):
		return player.getClient().getConnection().getInetAddress().getHostAddress()

	def onKill(self, npc, player, isPet): #��Ǫ��Q���� �|�Q�I�s.. player �O���M���Ǫ����a
		party = player.getParty() #��o���M���a������
		if party: #�p�G���ն����p
			members = [] #��l�� �����ܼ�
			cc = party.getCommandChannel() #���o �p�x (�p�G��)
			if cc: #���p�x
				members = cc.getMembers() #���o�p�x�Ҧ�����
			else: #�S���p�x
				members = party.getMembers() #���o�@�붤��Ҧ�����
			ipDict = {}
			for m in members:
				ipDict[self.getIP(m)] = ''
			if len(ipDict) != len(members):	#���խ��� IP �ۦP. �S���S�O���y
				return
			for m in members: #�b members �ܼƨ��X�C�Ӧ��� M
				if Util.checkIfInRange(2000, player, m, False): #�p�� ���� M �� ���M���a���Z�� �O�_�b 2000 ���H��
					for itemid, minc, maxc, c in self.REWARD:
						if self.getRandom(1000000) <= c*10000:
							m.addItem(self.qn, itemid, self.getRandom(minc, maxc), None, True)
				else: #�Z�����b 2000 ���H��
					self.sendMessage(player, "���b�d�� �����S�O���y") #�V���a�o�X�T��
		else: #�p�G�S���ն����p
			self.sendMessage(player, "�S������ �����S�O���y") #�V���a�o�X�T��

Quest() #�I�s Quest �� __init__