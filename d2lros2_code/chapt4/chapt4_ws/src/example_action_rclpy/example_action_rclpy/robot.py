from robot_control_interfaces.action import MoveRobot
import math

class Robot():
    def __init__(self) -> None:
        self.current_pose_ = 0.0 
        self.target_pose_ = 0.0
        self.move_distance_ = 0.0
        self.status_ = MoveRobot.Feedback.STATUS_STOP

    def get_status(self):
        return self.status_

    def get_current_pose(self):
        return self.current_pose_

    def close_goal(self):
        return math.fabs(self.target_pose_ - self.current_pose_) < 0.01

    def stop_move(self):
        self.status_ = MoveRobot.Feedback.STATUS_STOP

    def move_step(self):
        direct = self.move_distance_ / math.fabs(self.move_distance_)
        step = direct *math.fabs(self.target_pose_ - self.current_pose_)*0.1
        self.current_pose_ += step
        print(f"移动了：{step}，当前位置：{self.current_pose_}")
        return self.current_pose_

    def set_goal(self,distance):
        self.move_distance_ = distance
        self.target_pose_ += distance

        if self.close_goal():
            self.stop_move
            return False
        
        self.status_ = MoveRobot.Feedback.STATUS_MOVING
        return True

if __name__ == '__main__':
    main()