from archers.utils import EventsMixins
from archers.messages import message_types, UpdateMessage, FrameMessage, RemoveMessage
import struct
from archers.utils import m2p, limit


class Connection(EventsMixins):
	def __init__(self, world):
		self.world = world
		self.known = dict()
		self.last_world_index = 0
		self.last_frame_index = 0
		self.world.on('destroy_object', self.on_destroy)
		self.world.on('step', self.on_update)
		self.world.on('step', self.frame_maybe)

	def on_update(self, world):
		if(self.last_world_index != world.object_index.index):
			messages = list()
			for index in range(self.last_world_index, world.object_index.index):
				index = index+1
				world_object = world.get_object_by_id(index)
				if(hasattr(world_object, 'physics')):
					msg = UpdateMessage()
					# msg['name'] = world_object.name
					msg['id'] = world_object.id
					msg['entity_type'] = world_object.__class__.__name__
					msg['width'] = limit(m2p(world_object.width))
					msg['height'] = limit(m2p(world_object.height))
					msg['x'] = limit(m2p(world_object.physics.position.x))
					msg['y'] = limit(m2p(world_object.physics.position.y))
					msg['direction'] = world_object.physics.angle
					msg['state'] = 0
					messages.append(msg)
				self.last_world_index = index
			self.trigger('update', messages)

	def on_destroy(self, id):
		messages = list()
		msg = RemoveMessage()
		msg['id'] = id
		messages.append(msg)
		self.trigger('remove', messages)

	def frame_maybe(self, world):
		self.trigger('frame', self.get_frame())

	# redundant, just reset the counter on_update?
	# def get_full_update(self):
	# 	update = UpdateMessage()
	# 	for item in self.world.object_index.values():
	# 		if(hasattr(item, 'physics')):
	# 			data = dict()
	# 			data['name'] = item.name
	# 			data['id'] = item.id
	# 			data['center'] = False
	# 			update[item.id] = data
	# 	return update

	def get_frame(self, updated_only=True):
		update = list()

		for item in self.world.object_index.values():
			if(hasattr(item, 'physics')):
				data = FrameMessage()
				data['id'] = item.id
				data['x'] = limit(m2p(item.physics.position.x))
				data['y'] = limit(m2p(item.physics.position.y))
				data['direction'] = item.physics.angle
				data['state'] = 0
				if not(item in self.known.keys() and self.known[item] == data):
					update.append(data)
					self.known[item] = data
		return update


def pack_messages(messages):
	if(len(messages) == 0):
		return ''

	buffer_ = struct.pack('B', messages[0].schema['id'])
	for message in messages:
		buffer_ += message.pack()
	return buffer_


def unpack_mesages(data):
	buffer_ = buffer(data)
	messages = list()
	message_cls = message_types[struct.unpack('B', buffer_[0])[0]]
	message_count = (len(buffer_)-1)/message_cls.get_byte_length()
	for i in range(message_count):
		msg_buffer = buffer_[1+i*message_cls.get_byte_length():1+(i+1)*message_cls.get_byte_length()]
		messages.append(message_cls.from_packed(msg_buffer))
	return messages
