#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};


#[link(name = "rebot_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__rebot_interfaces__msg__PalmTarget() -> *const std::ffi::c_void;
}

#[link(name = "rebot_interfaces__rosidl_generator_c")]
extern "C" {
    fn rebot_interfaces__msg__PalmTarget__init(msg: *mut PalmTarget) -> bool;
    fn rebot_interfaces__msg__PalmTarget__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<PalmTarget>, size: usize) -> bool;
    fn rebot_interfaces__msg__PalmTarget__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<PalmTarget>);
    fn rebot_interfaces__msg__PalmTarget__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<PalmTarget>, out_seq: *mut rosidl_runtime_rs::Sequence<PalmTarget>) -> bool;
}

// Corresponds to rebot_interfaces__msg__PalmTarget
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// Palm target + pinch state (vision_node -> servo_node)

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct PalmTarget {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::rmw::Header,

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
    unsafe {
      let mut msg = std::mem::zeroed();
      if !rebot_interfaces__msg__PalmTarget__init(&mut msg as *mut _) {
        panic!("Call to rebot_interfaces__msg__PalmTarget__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for PalmTarget {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rebot_interfaces__msg__PalmTarget__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rebot_interfaces__msg__PalmTarget__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rebot_interfaces__msg__PalmTarget__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for PalmTarget {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for PalmTarget where Self: Sized {
  const TYPE_NAME: &'static str = "rebot_interfaces/msg/PalmTarget";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__rebot_interfaces__msg__PalmTarget() }
  }
}


