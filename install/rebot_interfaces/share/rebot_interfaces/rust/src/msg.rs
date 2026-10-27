#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};



// Corresponds to rebot_interfaces__msg__PalmTarget
/// Palm target + pinch state (vision_node -> servo_node)

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct PalmTarget {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::Header,

    /// Palm 3D position in camera frame (m); invalid when visible=false
    pub position: [f32; 3],

    /// Frame valid = detected/bridged and depth passed the protection chain
    pub visible: bool,

    /// Depth-frozen frame (z is placeholder; servo skips KF update)
    pub frozen: bool,

    /// Optical-flow bridged frame (MediaPipe miss, LK fills in)
    pub bridged: bool,

    /// Consecutive lost frames (detector's view)
    pub lost: i32,

    /// Gripper target angle (degrees); invalid when pinch_valid=false
    pub pinch_deg: f64,


    // This member is not documented.
    #[allow(missing_docs)]
    pub pinch_valid: bool,

}



impl Default for PalmTarget {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::PalmTarget::default())
  }
}

impl rosidl_runtime_rs::Message for PalmTarget {
  type RmwMsg = super::msg::rmw::PalmTarget;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Owned(msg.header)).into_owned(),
        position: msg.position,
        visible: msg.visible,
        frozen: msg.frozen,
        bridged: msg.bridged,
        lost: msg.lost,
        pinch_deg: msg.pinch_deg,
        pinch_valid: msg.pinch_valid,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Borrowed(&msg.header)).into_owned(),
        position: msg.position,
      visible: msg.visible,
      frozen: msg.frozen,
      bridged: msg.bridged,
      lost: msg.lost,
      pinch_deg: msg.pinch_deg,
      pinch_valid: msg.pinch_valid,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      header: std_msgs::msg::Header::from_rmw_message(msg.header),
      position: msg.position,
      visible: msg.visible,
      frozen: msg.frozen,
      bridged: msg.bridged,
      lost: msg.lost,
      pinch_deg: msg.pinch_deg,
      pinch_valid: msg.pinch_valid,
    }
  }
}


