#!/usr/bin/env python
import sys
import rospy
import numpy as np
import traceback
import time
import copy

from moveit_msgs.msg import OrientationConstraint
from geometry_msgs.msg import PoseStamped

from path_planner import PathPlanner
from controller import Controller
from intera_interface import Limb

from planning.msg import ChouChou

queue = []
prev_msg = ""

def get_points(message):
	"""
	We will add the point we received to queue
	"""
	global prev_msg
	
	#print("9999",message.status_type)
	if prev_msg != message and message.status_type != "dummy":
		queue.append(message)
		prev_msg = message

def main():
	plandraw = PathPlanner('right_arm')

	plandraw.start_position()

	## BOX
	box_size = np.array([2.4,2.4,0.1])
	box_pose = PoseStamped()
	box_pose.header.stamp = rospy.Time.now()
	box_pose.header.frame_id = "base"
	box_pose.pose.position.x = 0
	box_pose.pose.position.y = 0
	box_pose.pose.position.z = -0.4
	box_pose.pose.orientation.x = 0.00
	box_pose.pose.orientation.y = 0.00
	box_pose.pose.orientation.z = 0.00
	box_pose.pose.orientation.w = 1.00
	plandraw.add_box_obstacle(box_size,"box1",box_pose)

	box_size2 = np.array([2.4,2.4,0.1])
	box_pose2 = PoseStamped()
	box_pose2.header.stamp = rospy.Time.now()
	box_pose2.header.frame_id = "base"
	box_pose2.pose.position.x = 0
	box_pose2.pose.position.y = 0
	box_pose2.pose.position.z = 1
	box_pose2.pose.orientation.x = 0.00
	box_pose2.pose.orientation.y = 0.00
	box_pose2.pose.orientation.z = 0.00
	box_pose2.pose.orientation.w = 1.00
	plandraw.add_box_obstacle(box_size2,"box2",box_pose2)


	orien_const = OrientationConstraint()
	orien_const.link_name = "right_gripper_tip";
	orien_const.header.frame_id = "base";
	orien_const.orientation.y = -1.0;
	orien_const.absolute_x_axis_tolerance = 0.1;
	orien_const.absolute_y_axis_tolerance = 0.1;
	orien_const.absolute_z_axis_tolerance = 0.1;
	orien_const.weight = 1.0;

	while not rospy.is_shutdown():
		#raw_input("~~~~~~~~~~~~!!!!!!!!!!!!")
		while not rospy.is_shutdown():
			try:
				while queue:
					cur = queue[0]
					x,y,z = cur.position_x,cur.position_y,cur.position_z
					if cur.status_type != "edge_grad":
						# ti bi !!!!! luo bi !!!!
						if cur.status_type == "starting":
							print("start")
							goal_1 = PoseStamped()
							goal_1.header.frame_id = "base"

							#x, y, and z position
							goal_1.pose.position.x = x
							goal_1.pose.position.y = y
							goal_1.pose.position.z = z

							#Orientation as a quaternion
							goal_1.pose.orientation.x = 0.0
							goal_1.pose.orientation.y = -1.0
							goal_1.pose.orientation.z = 0.0
							goal_1.pose.orientation.w = 0.0



							waypoints = []
							waypoints.append(copy.deepcopy(goal_1.pose))

							plan = plandraw.plan_to_pose(goal_1, [orien_const], waypoints)

							if not plandraw.execute_plan(plan):
								raise Exception("Starting execution failed")
							else:
								queue.pop(0)
						elif cur.status_type == "next_point":
							print("next")
							goal_1 = PoseStamped()
							goal_1.header.frame_id = "base"

							#x, y, and z position
							goal_1.pose.position.x = x
							goal_1.pose.position.y = y
							goal_1.pose.position.z = z

							#Orientation as a quaternion
							goal_1.pose.orientation.x = 0.0
							goal_1.pose.orientation.y = -1.0
							goal_1.pose.orientation.z = 0.0
							goal_1.pose.orientation.w = 0.0


							waypoints = []
							waypoints.append(copy.deepcopy(goal_1.pose))

							plan = plandraw.plan_to_pose(goal_1, [orien_const], waypoints)

							if not plandraw.execute_plan(plan):
								raise Exception("Execution failed, point is ", cur)
							else:
								queue.pop(0)
						elif cur.status_type == "ending":
							print("prev_msg      ",prev_msg)
							goal_1 = PoseStamped()
							goal_1.header.frame_id = "base"

							#x, y, and z position
							goal_1.pose.position.x = prev_msg.position_x
							goal_1.pose.position.y = prev_msg.position_y 
							goal_1.pose.position.z = prev_msg.position_z - 0.078

							#Orientation as a quaternion
							goal_1.pose.orientation.x = 0.0
							goal_1.pose.orientation.y = -1.0
							goal_1.pose.orientation.z = 0.0
							goal_1.pose.orientation.w = 0.0

							#plan = plandraw.plan_to_pose(goal_1, [orien_const])
							# if not plandraw.execute_plan(plan):
							# 	raise Exception("Execution failed")
							print("ti bi")
							queue.pop(0)
				#raw_input("Press <Enter> to move next!!!")
			except Exception as e:
				print e
			else:
				#print("lllllllllllllllllllll")
				break



if __name__ == '__main__':
	rospy.init_node('moveit_node')
	rospy.Subscriber("position_messages", ChouChou, get_points, queue_size=10)
	
	main()
	rospy.spin()
