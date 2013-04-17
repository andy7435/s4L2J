import sys
from com.l2jserver.gameserver.model.quest		import State
from com.l2jserver.gameserver.model.quest		import QuestState
from com.l2jserver.gameserver.model.quest.jython	import QuestJython as JQuest

from com.l2jserver.gameserver.instancemanager import GrandBossManager
from com.l2jserver.gameserver.instancemanager import QuestManager

from com.l2jserver.gameserver.datatables import DoorTable #�ڦC���n��
from com.l2jserver.gameserver.network.serverpackets import Earthquake #�a�s�n��
from com.l2jserver.gameserver.model import L2World #�a�s�n��

from com.l2jserver.gameserver.datatables import SpawnTable
from com.l2jserver.gameserver.instancemanager import InstanceManager
from com.l2jserver.gameserver.datatables import ItemTable

import time
from com.l2jserver import L2DatabaseFactory

class GBreset(JQuest):
	qID = -1
	qn = "GBreset"
	qDesc = "custom"
	
	NPCID = [103] #Ĳ�o���Ȫ� NPC �i�ק�.. �i�H�h ID �Ҧp [100,102,103]
	htm_header = "<html><body><title>�Y�ح��⭫�m�t��</title>"
	htm_footer = "</body></html>"
	htm_no_rights = "<center>��p �A�S���v�����m</center>"
	htm_not_enough_item = "�һݹD�㤣��<BR>"

	zaken_INSTANCEID_NIGHT = 114
	zaken_INSTANCEID_DAY = 133
	zaken_INSTANCEID_DAY83 = 135
	
	reset_instance = [
		["����(�])", zaken_INSTANCEID_NIGHT, [[57,1]]]
		,["����(��)", zaken_INSTANCEID_DAY, [[57,1]]]
		,["����(�W��)", zaken_INSTANCEID_DAY83, [[57,1]]]
		,["�ܵY���F", 136, [[57,1]]]
		,["�ں���", 10, [[57,1]]]
	]
	
	available = "�i�D��"
	waiting = "���ݶ}�l"
	fighting = "���a�D�Ԥ�"
	dead = "���`"
	unknow = "�������A"
	
	def general_unlock(self, arg):
		quest_name, unlock_timer_name = arg
		if len(quest_name) > 0:
			q = QuestManager.getInstance().getQuest(quest_name)
			if len(unlock_timer_name) > 0:
				try:
					q.cancelQuestTimers(unlock_timer_name)
					q.startQuestTimer(unlock_timer_name, 1000, None, None)
				except:
					pass

	def antharas_unlock(self, arg):
		boss_id = arg[0]
		GrandBossManager.getInstance().setBossStatus(boss_id, 0)
		for p in L2World.getInstance().getAllPlayersArray():
			p.broadcastPacket(Earthquake(185708,114298,-8221,20,10))

	def beleth_unlock(self, arg):
		GrandBossManager.getInstance().setBossStatus(29118, 0)
		DoorTable.getInstance().getDoor(20240001).openMe()
		
	def icefairysirra_unlock(self):
		q = QuestManager.getInstance().getQuest("IceFairySirra")
		self.saveGlobalQuestVar("Sirra_Respawn", "0")
		try:
			q.cancelQuestTimers("respawn")
			q.startQuestTimer("respawn", 1000, None, None)
		except:
			pass
			
	def reset_queststate(self, player, quest_name):
		qs = player.getQuestState(quest_name)
		if qs:
			qs.setState(State.STARTED);
			qs.exitQuest(True)
			if quest_name == "10286_ReunionWithSirra":
				q = QuestManager.getInstance().getQuest("10286_ReunionWithSirra")
				st = player.getQuestState(quest_name)
				if not st:
					st = q.newQuestState(player)
					st.setState(State.STARTED)
				st.set("cond", "1")
				st.set("cond", "2")
				st.set("cond", "3")
				st.set("cond", "4")
				st.set("cond", "5")
				st.set("Ex", "2")
				st.set("progress", "2")

	gb_list = dict({
	29001:["���Ƥk��", [available, dead], [general_unlock, "queen_ant", "queen_unlock"]], 
	29006:["�֤�", [available, dead], [general_unlock, "core", "core_unlock"]],
	29014:["������", [available, dead], [general_unlock, "orfen", "orfen_unlock"]],
	29019:["�w��紵", [available, waiting, fighting, dead], [antharas_unlock, 29019]],
	29020:["�ڷ�", [available, fighting, dead], [general_unlock, "baium", "baium_unlock"]],
	#29022:["����", [available, dead], [general_unlock, "zaken", "zaken_unlock"]],
	29028:["�کԥd��", [available, waiting, fighting, dead], [general_unlock, "valakas", "valakas_unlock"]],
	#29045:["�ܵY���F", [available, dead], [general_unlock, "", ""]],
	29065:["�ɺ���", [available, waiting, fighting, dead], [general_unlock, "sailren", "sailren_unlock"]],
	29066:["�w��紵", [available, waiting, fighting, dead], [antharas_unlock, 29066]],
	29067:["�w��紵", [available, waiting, fighting, dead], [antharas_unlock, 29067]],
	29068:["�w��紵", [available, waiting, fighting, dead], [antharas_unlock, 29068]],
	#29099:["�ں���", [available, dead], [general_unlock, "", ""]],
	29118:["�ڦC��", [available, waiting, fighting, dead], [beleth_unlock]]
	})
	

	def __init__(self, id = qID, name = qn, descr = qDesc):
		JQuest.__init__(self, id, name, descr)
		for id in self.NPCID:
			self.addStartNpc(id)
			self.addFirstTalkId(id)
			self.addTalkId(id)
		print "Init:" + self.qn + " loaded"

	def getNpcInstance(self, npc_id):
		spawnTable = SpawnTable.getInstance()
		for spawn in spawnTable.getSpawnTable():
			if spawn.getNpcid() == npc_id:
				return spawn.getLastSpawn()
		return None
		
	def get_STEWARD_state(self):
		npc = self.getNpcInstance(32029) #������������
		if npc:
			return npc.isBusy()
		return None
		
	def get_GB_respawn_time(self):
		r = {}
		con, statement, rset = None, None, None
		try:
			con = L2DatabaseFactory.getInstance().getConnection()
			statement = con.prepareStatement("select `boss_id`, `respawn_time` from `grandboss_data`;")
			rset = statement.executeQuery()
			while rset.next():
				r[rset.getInt("boss_id")] = rset.getLong("respawn_time")
		finally:
			if rset:
				rset.close()
			if statement:
				statement.close()
			if con:
				L2DatabaseFactory.close(con)
		return r
		
	def get_gbrt_string(self, rt):
		try:
			r = long(long(rt)/1000 - time.time())
			s = long(r) % 60
			m = (long(r) / 60) % 60
			h = (long(r) / (60*60)) % 24
			d = (long(r) / (60*60*24))
			return "%d�� %d�� %d�� %d��" % (d, h, m, s)
		except:
			return "�S���ɶ��ƾ�"
		
		
	def htm_list(self):
		gbrt = self.get_GB_respawn_time()
		r = ""
		for key in self.gb_list.keys():
			boss_name, boss_status, dummy = self.gb_list[key]
			curr_status = GrandBossManager.getInstance().getBossStatus(key)
			if len(boss_status)-1 == curr_status:
				r += "<tr><td width=100>" + boss_name + "(" + str(key)+ ")" + "</td><td width=150><a action=\"bypass -h Quest " + self.qn + " " + str(key)+ "\">" + self.get_gbrt_string(gbrt[key]) + "</a></td></tr>"
			else:
				r += "<tr><td width=100>" + boss_name + "(" + str(key)+ ")" + "</td><td>" + boss_status[curr_status] + "</td></tr>"
		# if self.get_STEWARD_state():
			# r += "<tr><td width=100>" + "������������" + "</td><td><a action=\"bypass -h Quest " + self.qn + " " + "IFS" + "\">" + " �� " + "</a></td></tr>"
		# else:
			# r += "<tr><td width=100>" + "������������" + "</td><td>" + "��" + "</td></tr>"
		r += "<tr><td width=100>" + "�P���S�A������" + "</td><td><a action=\"bypass -h Quest " + self.qn + " " + "reset 10286_ReunionWithSirra" + "\">" + " ���m���� " + "</a></td></tr>"
		for instance_name, instance_id, require in self.reset_instance:
			r += "<tr><td width=100>" + instance_name + "</td><td><a action=\"bypass -h Quest " + self.qn + " " + "show_require " + str(instance_id) + "\">" + " ���m�ƥ��ɶ�" + "</a></td></tr>"
		return self.htm_header + "<table>" + r + "</table>" + self.htm_footer

		
	def show_require_item(self, instance_id):
		r = "�ݭn�D��M��<br>"
		for instance_name,rinstance_id,require_list in self.reset_instance:
			if str(rinstance_id) == instance_id:
				for itemid, count in require_list:
					item_name = ItemTable.getInstance().getTemplate(itemid).getName()
					r += "%s %d ��<br1>" % (item_name, count)
				break
		r += '<a action="bypass -h Quest %s del_instance %d">�T�{���m %s</a>' % (self.qn, instance_id, instance_name)
		return r
		
		
	def check_require_item(self, player, require_list):
		st = player.getQuestState(self.qn)
		if not st: return False
		for itemid, count in require_list:
			if st.getQuestItemsCount(itemid) < count:
				item_name = ItemTable.getInstance().getTemplate(itemid).getName()
				player.sendMessage("�D�㤣��:" + item_name + " �ݭn " + str(count))
				return False
		return True

	def deleteInstanceTime(self, player_oid, instance_id):
		st = player.getQuestState(self.qn)
		if not st: return False
		for dummy,rinstance_id,require in self.reset_instance:
			if str(rinstance_id) == instance_id:
				if not self.check_require_item(player, require):
					return self.htm_header + self.htm_not_enough_item + self.htm_footer
				map(lambda (item_id, count): st.takeItems(item_id, count), require)
				InstanceManager.getInstance().deleteInstanceTime(player.getObjectId(), rinstance_id)
				break
		
	def onAdvEvent(self, event, npc, player):
		try:
			nEvent = int(event)
		except:
			nEvent = -1
			
		if nEvent in self.gb_list.keys():
			if player.isGM():
				self.gb_list[nEvent][2][0](self, self.gb_list[nEvent][2][1:])
			else:
				return self.htm_header + self.htm_no_rights + self.htm_footer
		if event == "IFS":
			if player.isGM():
				self.icefairysirra_unlock()
			else:
				return self.htm_header + self.htm_no_rights + self.htm_footer
		if event.startswith("reset "):
			event = event.split()[1]
			self.reset_queststate(player, event)
		if event.startswith("show_require "):
			event = event.split()[1]
			return self.htm_header + self.show_require_item(event) + self.htm_footer
		if event.startswith("del_instance "):
			st = player.getQuestState(self.qn)
			event = event.split()[1]
			for dummy,instance_id,require in self.reset_instance:
				if str(instance_id) == event:
					if not self.check_require_item(player, require):
						return self.htm_header + self.htm_not_enough_item + self.htm_footer
					map(lambda (item_id, count): st.takeItems(item_id, count), require)	
					InstanceManager.getInstance().deleteInstanceTime(player.getObjectId(), int(event))
					break
		return self.onFirstTalk(npc, player)
		
	def onFirstTalk(self, npc, player):
		st = player.getQuestState(self.qn)
		if not st:
			st = self.newQuestState(player)
			st.setState(State.STARTED)
		return self.htm_list()
		
GBreset()
