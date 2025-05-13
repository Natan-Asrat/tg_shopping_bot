
def on_buy_button_clicked_checking_availability(post_text):
    return f"{post_text}\n\n{'='*30}\n\n🔍 Checking availability... Please wait"

def on_availability_check_request(post_text):
    return f"🛒 Availability Check Request\n\nIs this item still available?\n\n{post_text}"

def on_notified_seller_response():
    return "📬 We've notified the seller about your request. They'll respond shortly!"

def on_couldnt_reach_seller_edit_post(post_text):
    return f"{post_text}\n\n{'='*30}\n\n⚠️ Couldn't process your request. Please try again."

def on_couldnt_reach_seller_new_response():
    return "⚠️ Couldn't reach seller. Please try again later."

def on_confirm_availability_edit_text_for_seller(post_text):
    return f"{post_text}\n\n{'='*30}\n\n✅ Item is available. The buyer will contact you soon if they are sure."

def on_confirm_availability_edit_text_for_buyer(post_text):
    return f"{post_text}\n\n{'='*30}\n\n✅ Item is available! You can proceed with your purchase."

def on_confirmed_availability_response():
    return "✅ Good news! The item you inquired about is available.\n\n⚠️ IMPORTANT: If you proceed and don't complete the purchase, you will be banned from using this service for 7 days."

def on_responded_sure_buy():
    return f"{on_confirmed_availability_response()}\n\n{'='*30}\n\n✅ You have confirmed to proceed with the purchase.\nPlease complete the transaction to avoid any penalties."

def on_deny_availability_edit_text_for_seller(post_text):
    return f"{post_text}\n\n{'='*30}\n\n❌ Item is not available"

def on_deny_availability_response():
    return "❌ Sorry, this item is currently not available."

def on_deny_availability_edit_text_for_buyer(post_text):
    return f"{post_text}\n\n{'='*30}\n\n❌ Sorry, this item is not available at the moment."
