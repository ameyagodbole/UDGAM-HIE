/**
 * @file offb_node.cpp
 * @brief offboard example node, written with mavros version 0.14.2, px4 flight
 * stack and tested in Gazebo SITL
 */

#include <ros/ros.h>
#include <geometry_msgs/PoseStamped.h>
#include <mavros_msgs/SetMode.h>
#include <mavros_msgs/CommandBool.h>
#include <mavros_msgs/State.h>
#include <mavros_msgs/GlobalPositionTarget.h>
#include <sensor_msgs/NavSatFix.h>

mavros_msgs::State current_state;
sensor_msgs::NavSatFix current_gps_state;

void state_cb(const mavros_msgs::State::ConstPtr& msg){
    current_state = *msg;
}

void gps_state_cb(const sensor_msgs::NavSatFix::ConstPtr& msg){
    current_gps_state = *msg;
}

int main(int argc, char **argv)
{
    ros::init(argc, argv, "offb_node");
    ros::NodeHandle nh;

    ros::Subscriber state_sub = nh.subscribe<mavros_msgs::State>
            ("mavros/state", 10, state_cb);
    ros::Subscriber global_gps_sub = nh.subscribe<sensor_msgs::NavSatFix>
            ("mavros/global_position/global", 10, gps_state_cb);
    ros::Publisher local_pos_pub = nh.advertise<geometry_msgs::PoseStamped>
            ("mavros/setpoint_position/local", 10);
    ros::ServiceClient arming_client = nh.serviceClient<mavros_msgs::CommandBool>
            ("mavros/cmd/arming");
    ros::ServiceClient set_mode_client = nh.serviceClient<mavros_msgs::SetMode>
            ("mavros/set_mode");

    //the setpoint publishing rate MUST be faster than 2Hz
    ros::Rate rate(20.0);

    // wait for FCU connection
    while(ros::ok() && !current_state.connected){
        ros::spinOnce();
        rate.sleep();
    }

    mavros_msgs::GlobalPositionTarget target;
    target.latitude = 100;
    target.longitude = 20;
    target.altitude = 600;

    geometry_msgs::PoseStamped pose;
    pose.pose.position.x = 0;
    pose.pose.position.y = 0;
    pose.pose.position.z = 0;

    //send a few setpoints before starting
    for(int i = 100; ros::ok() && i > 0; --i){
        local_pos_pub.publish(pose);
        ros::spinOnce();
        rate.sleep();
    }

    mavros_msgs::SetMode offb_set_mode;
    offb_set_mode.request.custom_mode = "OFFBOARD";

    mavros_msgs::CommandBool arm_cmd;
    arm_cmd.request.value = true;

    ros::Time last_request = ros::Time::now();
    ros::Time start = ros::Time::now();

    while(ros::ok()){
        if( current_state.mode != "OFFBOARD" &&
            (ros::Time::now() - last_request > ros::Duration(5.0))){
            if( set_mode_client.call(offb_set_mode) &&
                offb_set_mode.response.success){
                ROS_INFO("Offboard enabled");
            }
            last_request = ros::Time::now();
        } else {
            if( !current_state.armed &&
                (ros::Time::now() - last_request > ros::Duration(5.0))){
                if( arming_client.call(arm_cmd) &&
                    arm_cmd.response.success){
                    ROS_INFO("Vehicle armed");
                }
                last_request = ros::Time::now();
            }
        }

        pose.pose.position.x = sqrt(target.latitude - current_gps_state.latitude);
        pose.pose.position.y = sqrt(target.longitude - current_gps_state.longitude);
        pose.pose.position.z = (target.altitude - current_gps_state.altitude)/10;

        if()

        local_pos_pub.publish(pose);

        //LANDING AFTER 20 SECONDS
        // if(ros::Time::now() - start > ros::Duration(30)){
        //     offb_set_mode.request.custom_mode = "AUTO.RTL";
        //     if(set_mode_client.call(offb_set_mode) && offb_set_mode.response.success){
        //         ROS_INFO("LANDING");
        //         break;
        //     }
        // }

        ros::spinOnce();
        rate.sleep();
    }
    ros::Duration(10).sleep();
    arm_cmd.request.value=false;
    arming_client.call(arm_cmd);
    ROS_INFO("Disarmed");


    return 0;
}
