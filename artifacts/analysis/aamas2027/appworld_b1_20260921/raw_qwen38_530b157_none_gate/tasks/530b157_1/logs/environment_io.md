
### Environment Interaction 1
----------------------------------------------------------------------------
```python
print(apis.api_docs.show_app_descriptions())
```

```
[
 {
  "name": "api_docs",
  "description": "An app to search and explore API documentation."
 },
 {
  "name": "supervisor",
  "description": "An app to access supervisor's personal information, account credentials, addresses, payment cards, and manage the assigned task."
 },
 {
  "name": "amazon",
  "description": "An online shopping app to buy products and manage orders, returns, etc."
 },
 {
  "name": "phone",
  "description": "An app to find and manage contact information for friends, family members, etc., send and receive messages, and manage alarms."
 },
 {
  "name": "file_system",
  "description": "A file system app to create and manage files and folders."
 },
 {
  "name": "spotify",
  "description": "A music streaming app to stream songs and manage song, album and playlist libraries."
 },
 {
  "name": "venmo",
  "description": "A social payment app to send, receive and request money to and from others."
 },
 {
  "name": "gmail",
  "description": "An email app to draft, send, receive, and manage emails."
 },
 {
  "name": "splitwise",
  "description": "A bill splitting app to track and split expenses with people."
 },
 {
  "name": "simple_note",
  "description": "A note-taking app to create and manage notes."
 },
 {
  "name": "todoist",
  "description": "A task management app to manage todo lists and collaborate on them with others."
 }
]
```


### Environment Interaction 2
----------------------------------------------------------------------------
```python
print(apis.api_docs.show_api_descriptions(app_name='phone'))
print(apis.api_docs.show_api_descriptions(app_name='venmo'))
```

```
[
 {
  "name": "show_account",
  "description": "Show your account information. Unlike show_profile, this includes private information."
 },
 {
  "name": "signup",
  "description": "Sign up to create account."
 },
 {
  "name": "delete_account",
  "description": "Delete your account."
 },
 {
  "name": "update_account_name",
  "description": "Update your first or last name in the account profile."
 },
 {
  "name": "login",
  "description": "Login to your account."
 },
 {
  "name": "logout",
  "description": "Logout from your account."
 },
 {
  "name": "send_password_reset_code",
  "description": "Send password reset code to your phone number."
 },
 {
  "name": "reset_password",
  "description": "Reset your password using the password reset code sent to your email address."
 },
 {
  "name": "show_profile",
  "description": "Show public profile information of a user."
 },
 {
  "name": "show_contact_relationships",
  "description": "Get a list of all relationships available in your contact book."
 },
 {
  "name": "search_contacts",
  "description": "Search your contact book for relatives' information."
 },
 {
  "name": "add_contact",
  "description": "Add a new contact."
 },
 {
  "name": "update_contact",
  "description": "Update contact information."
 },
 {
  "name": "delete_contact",
  "description": "Delete contact information."
 },
 {
  "name": "show_text_message_window",
  "description": "Show text messages with a contact around a given date and time."
 },
 {
  "name": "search_text_messages",
  "description": "Show or search your text messages."
 },
 {
  "name": "show_text_message",
  "description": "Show text message details."
 },
 {
  "name": "delete_text_message",
  "description": "Delete a text message."
 },
 {
  "name": "send_text_message",
  "description": "Send a text message on the given phone number."
 },
 {
  "name": "show_alarms",
  "description": "Get a list of alarms."
 },
 {
  "name": "create_alarm",
  "description": "Create a new alarm."
 },
 {
  "name": "show_alarm",
  "description": "Show alarm details."
 },
 {
  "name": "update_alarm",
  "description": "Update an alarm's settings."
 },
 {
  "name": "delete_alarm",
  "description": "Delete an alarm."
 },
 {
  "name": "show_voice_message_window",
  "description": "Show voice messages with a contact around a given date and time."
 },
 {
  "name": "search_voice_messages",
  "description": "Show or search text voice_messages between the user and a contact."
 },
 {
  "name": "show_voice_message",
  "description": "Show voice message details."
 },
 {
  "name": "delete_voice_message",
  "description": "Delete a voice message."
 },
 {
  "name": "send_voice_message",
  "description": "Send a voice message on the given phone number."
 },
 {
  "name": "get_current_date_and_time",
  "description": "Show current date and time."
 }
]
[
 {
  "name": "show_account",
  "description": "Show your account information. Unlike show_profile, this includes private information."
 },
 {
  "name": "signup",
  "description": "Sign up to create account."
 },
 {
  "name": "delete_account",
  "description": "Delete your account."
 },
 {
  "name": "update_account_name",
  "description": "Update your first or last name in the account profile."
 },
 {
  "name": "login",
  "description": "Login to your account."
 },
 {
  "name": "logout",
  "description": "Logout from your account."
 },
 {
  "name": "send_verification_code",
  "description": "Send account verification code to your email address."
 },
 {
  "name": "verify_account",
  "description": "Verify your account using the verification code sent to your email address."
 },
 {
  "name": "send_password_reset_code",
  "description": "Send password reset code to your email address."
 },
 {
  "name": "reset_password",
  "description": "Reset your password using the password reset code sent to your email address."
 },
 {
  "name": "show_profile",
  "description": "Show public profile information of a user, including your friendship status with them."
 },
 {
  "name": "search_users",
  "description": "Search Venmo users by name or email address."
 },
 {
  "name": "search_friends",
  "description": "Search your or others' friends by name or email address."
 },
 {
  "name": "add_friend",
  "description": "Add a friend to your friend list."
 },
 {
  "name": "remove_friend",
  "description": "Remove a friend from your friend list."
 },
 {
  "name": "add_to_venmo_balance",
  "description": "Add money to your Venmo balance."
 },
 {
  "name": "show_venmo_balance",
  "description": "Show your Venmo balance."
 },
 {
  "name": "withdraw_from_venmo_balance",
  "description": "Withdraw money from your Venmo balance."
 },
 {
  "name": "show_bank_transfer_history",
  "description": "Show histroy of money transfer from Venmo to payment card and vice versa."
 },
 {
  "name": "download_bank_transfer_receipt",
  "description": "Download the receipt of money transfer from Venmo to payment card or vice versa."
 },
 {
  "name": "show_transaction",
  "description": "Show transaction details."
 },
 {
  "name": "update_transaction",
  "description": "Update transaction information."
 },
 {
  "name": "create_transaction",
  "description": "Send money to a user."
 },
 {
  "name": "show_transactions",
  "description": "Search or show a list of your transactions."
 },
 {
  "name": "download_transaction_receipt",
  "description": "Download the receipt of a transaction (money sent from one user to another)."
 },
 {
  "name": "like_transaction",
  "description": "Like a transaction."
 },
 {
  "name": "unlike_transaction",
  "description": "Unlike a transaction."
 },
 {
  "name": "show_transaction_comments",
  "description": "Get a list of transaction comments."
 },
 {
  "name": "create_transaction_comment",
  "description": "Create a new transaction comment."
 },
 {
  "name": "show_transaction_comment",
  "description": "Show detailed information about a transaction comment."
 },
 {
  "name": "update_transaction_comment",
  "description": "Update a transaction comment."
 },
 {
  "name": "delete_transaction_comment",
  "description": "Delete a transaction comment."
 },
 {
  "name": "like_transaction_comment",
  "description": "Like a transaction comment."
 },
 {
  "name": "unlike_transaction_comment",
  "description": "Unlike a previously liked transaction comment."
 },
 {
  "name": "show_payment_card",
  "description": "Get details of a payment card."
 },
 {
  "name": "update_payment_card",
  "description": "Update payment card information."
 },
 {
  "name": "delete_payment_card",
  "description": "Delete payment card information."
 },
 {
  "name": "show_payment_cards",
  "description": "Get a list of users payment cards."
 },
 {
  "name": "add_payment_card",
  "description": "Add a new payment card."
 },
 {
  "name": "show_received_payment_requests",
  "description": "Search or show a list of payment requests you have received from others."
 },
 {
  "name": "show_sent_payment_requests",
  "description": "Search or show a list of payment requests you have sent to others."
 },
 {
  "name": "create_payment_request",
  "description": "Send a payment request."
 },
 {
  "name": "update_payment_request",
  "description": "Update payment request information."
 },
 {
  "name": "delete_payment_request",
  "description": "Delete a payment request."
 },
 {
  "name": "approve_payment_request",
  "description": "Approve a payment request."
 },
 {
  "name": "deny_payment_request",
  "description": "Deny a payment request."
 },
 {
  "name": "remind_payment_request",
  "description": "Send a reminder to a user via notification about this payment request."
 },
 {
  "name": "show_social_feed",
  "description": "Show your social feed (transactions of your friends)."
 },
 {
  "name": "show_notifications",
  "description": "Get a list of your notifications."
 },
 {
  "name": "delete_notifications",
  "description": "Delete all of your notifications."
 },
 {
  "name": "mark_notifications",
  "description": "Mark all notifications as read or unread."
 },
 {
  "name": "show_notifications_count",
  "description": "Get the count of your notifications."
 },
 {
  "name": "delete_notification",
  "description": "Delete a notification."
 },
 {
  "name": "mark_notification",
  "description": "Mark a notification as read or unread."
 }
]
```


### Environment Interaction 3
----------------------------------------------------------------------------
```python
print(apis.api_docs.show_api_descriptions(app_name='supervisor'))
```

```
[
 {
  "name": "show_active_task",
  "description": "Show the currently active task assigned to you by the supervisor."
 },
 {
  "name": "complete_task",
  "description": "Mark the currently active task as complete with the given answer."
 },
 {
  "name": "show_profile",
  "description": "Show your supervisor's profile information."
 },
 {
  "name": "show_addresses",
  "description": "Show your supervisor's addresses."
 },
 {
  "name": "show_payment_cards",
  "description": "Show your supervisor's payment_cards."
 },
 {
  "name": "show_account_passwords",
  "description": "Show your supervisor's app account passwords."
 }
]
```


### Environment Interaction 4
----------------------------------------------------------------------------
```python
passwords = apis.supervisor.show_account_passwords()
print(passwords)
```

```
[
 {
  "account_name": "amazon",
  "password": "Kv8O=+h"
 },
 {
  "account_name": "file_system",
  "password": "PpLu_dZ"
 },
 {
  "account_name": "gmail",
  "password": "%Czv-5s"
 },
 {
  "account_name": "phone",
  "password": "QG77Xz8"
 },
 {
  "account_name": "simple_note",
  "password": "3qCC2+8"
 },
 {
  "account_name": "splitwise",
  "password": "Z#{O$AI"
 },
 {
  "account_name": "spotify",
  "password": "TsivP)G"
 },
 {
  "account_name": "todoist",
  "password": "&M=jE1u"
 },
 {
  "account_name": "venmo",
  "password": "f$paRge"
 }
]
```


### Environment Interaction 5
----------------------------------------------------------------------------
```python
print(apis.api_docs.show_api_doc(app_name='phone', api_name='login'))
print(apis.api_docs.show_api_doc(app_name='venmo', api_name='login'))
```

```
{
 "app_name": "phone",
 "api_name": "login",
 "path": "/phone/auth/token",
 "method": "POST",
 "description": "Login to your account.",
 "parameters": [
  {
   "name": "username",
   "type": "string",
   "required": true,
   "description": "Your account phone_number.",
   "default": null,
   "constraints": []
  },
  {
   "name": "password",
   "type": "string",
   "required": true,
   "description": "Your account password.",
   "default": null,
   "constraints": []
  }
 ],
 "response_schemas": {
  "success": {
   "access_token": "string",
   "token_type": "string"
  },
  "failure": {
   "message": "string"
  }
 }
}
{
 "app_name": "venmo",
 "api_name": "login",
 "path": "/venmo/auth/token",
 "method": "POST",
 "description": "Login to your account.",
 "parameters": [
  {
   "name": "username",
   "type": "string",
   "required": true,
   "description": "Your account email.",
   "default": null,
   "constraints": []
  },
  {
   "name": "password",
   "type": "string",
   "required": true,
   "description": "Your account password.",
   "default": null,
   "constraints": []
  }
 ],
 "response_schemas": {
  "success": {
   "access_token": "string",
   "token_type": "string"
  },
  "failure": {
   "message": "string"
  }
 }
}
```


### Environment Interaction 6
----------------------------------------------------------------------------
```python
phone_login = apis.phone.login(username='4886643554', password='QG77Xz8')
venmo_login = apis.venmo.login(username='matthew.blac@gmail.com', password='f$paRge')
print(phone_login)
print(venmo_login)
```

```
{
 "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJwaG9uZSs0ODg2NjQzNTU0IiwiZXhwIjoxNjg0NDEyMDU4fQ.5pfrNo4TxoKG24j8q9lRaDA15ToOf4Yc2bd0cSx4vM8",
 "token_type": "Bearer"
}
{
 "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ2ZW5tbyttYXR0aGV3LmJsYWNAZ21haWwuY29tIiwiZXhwIjoxNjg0NDEyMTc2fQ.-EBuxeZyhWWGeq1rTe9b1sJHcQPxT426L6mmd3UdguI",
 "token_type": "Bearer"
}
```


### Environment Interaction 7
----------------------------------------------------------------------------
```python
phone_token = phone_login['access_token']
venmo_token = venmo_login['access_token']
contacts = apis.phone.search_contacts(access_token=phone_token, query='Kristin')
print(contacts)
```

```
[
 {
  "contact_id": 824,
  "first_name": "Kristin",
  "last_name": "White",
  "email": "kri-powe@gmail.com",
  "phone_number": "6017026518",
  "relationships": [
   "friend"
  ],
  "birthday": "1987-05-31",
  "home_address": "0031 Jeremy Cliff Suite 552\nSeattle\nWashington\nUnited States\n72731",
  "work_address": "7844 Joshua Shore Suite 460\nSeattle\nWashington\nUnited States\n46946",
  "created_at": "2022-05-10T22:56:32"
 },
 {
  "contact_id": 809,
  "first_name": "Paul",
  "last_name": "Miller",
  "email": "paul_mill@gmail.com",
  "phone_number": "3379617841",
  "relationships": [
   "coworker"
  ],
  "birthday": "1997-08-01",
  "home_address": "172 Matthew Knolls Suite 730\nSeattle\nWashington\nUnited States\n65644",
  "work_address": "265 Carpenter Loop Suite 064\nSeattle\nWashington\nUnited States\n44564",
  "created_at": "2022-05-10T22:56:32"
 },
 {
  "contact_id": 810,
  "first_name": "Denise",
  "last_name": "Maldonado",
  "email": "deniseburch@gmail.com",
  "phone_number": "6279200672",
  "relationships": [
   "coworker"
  ],
  "birthday": "1994-08-14",
  "home_address": "727 Cannon Falls Suite 933\nSeattle\nWashington\nUnited States\n74687",
  "work_address": "265 Carpenter Loop Suite 064\nSeattle\nWashington\nUnited States\n44564",
  "created_at": "2022-05-10T22:56:32"
 },
 {
  "contact_id": 811,
  "first_name": "Jeffery",
  "last_name": "Simpson",
  "email": "je.simpson@gmail.com",
  "phone_number": "9654124977",
  "relationships": [
   "coworker"
  ],
  "birthday": "1963-01-01",
  "home_address": "808 Richard Crescent Suite 750\nSeattle\nWashington\nUnited States\n18427",
  "work_address": "265 Carpenter Loop Suite 064\nSeattle\nWashington\nUnited States\n44564",
  "created_at": "2022-05-10T22:56:32"
 },
 {
  "contact_id": 812,
  "first_name": "Angelica",
  "last_name": "Wilson",
  "email": "angelica.wils@gmail.com",
  "phone_number": "6759633882",
  "relationships": [
   "coworker"
  ],
  "birthday": "1956-10-04",
  "home_address": "252 Nicole Light Suite 974\nSeattle\nWashington\nUnited States\n77751",
  "work_address": "265 Carpenter Loop Suite 064\nSeattle\nWashington\nUnited States\n44564",
  "created_at": "2022-05-10T22:56:32"
 }
]
```


### Environment Interaction 8
----------------------------------------------------------------------------
```python
print(apis.api_docs.show_api_doc(app_name='phone', api_name='search_text_messages'))
```

```
{
 "app_name": "phone",
 "api_name": "search_text_messages",
 "path": "/phone/messages/text",
 "method": "GET",
 "description": "Show or search your text messages.",
 "parameters": [
  {
   "name": "access_token",
   "type": "string",
   "required": true,
   "description": "Access token obtained from phone app login.",
   "default": null,
   "constraints": []
  },
  {
   "name": "query",
   "type": "string",
   "required": false,
   "description": "The search query string.",
   "default": "",
   "constraints": []
  },
  {
   "name": "phone_number",
   "type": "string",
   "required": false,
   "description": "The phone number of the contact to show messages with.",
   "default": null,
   "constraints": []
  },
  {
   "name": "only_latest_per_contact",
   "type": "boolean",
   "required": false,
   "description": "If set to true, only the latest message from each contact will be shown.",
   "default": false,
   "constraints": []
  },
  {
   "name": "page_index",
   "type": "integer",
   "required": false,
   "description": "The index of the page to return.",
   "default": 0,
   "constraints": [
    "value >= 0"
   ]
  },
  {
   "name": "page_limit",
   "type": "integer",
   "required": false,
   "description": "The maximum number of results to return per page.",
   "default": 5,
   "constraints": [
    "value >= 1, <= 20"
   ]
  },
  {
   "name": "sort_by",
   "type": "string",
   "required": false,
   "description": "The attribute to sort the messages by prefixed with +/- to reflect ascending/descending. Valid attributes: created_at. If both query and sort_by are given and non-empty, results will be first ranked by query relevance, then paginated, and will then be sorted by the given attribute within each page. If both query and sort_by are not given, null, or empty, sort_by will default to -created_at.",
   "default": null,
   "constraints": []
  }
 ],
 "response_schemas": {
  "success": [
   {
    "text_message_id": 1,
    "sender": {
     "contact_id": 1,
     "name": "string",
     "phone_number": "string"
    },
    "receiver": {
     "contact_id": 1,
     "name": "string",
     "phone_number": "string"
    },
    "message": "string",
    "sent_at": "2019-01-01T00:00:00"
   }
  ],
  "failure": {
   "message": "string"
  }
 }
}
```


### Environment Interaction 9
----------------------------------------------------------------------------
```python
current_dt = apis.phone.get_current_date_and_time(access_token=phone_token)
print(current_dt)
messages = apis.phone.search_text_messages(access_token=phone_token, phone_number='6017026518', page_index=0, page_limit=20, sort_by='-created_at')
print(messages)
```

```
Execution failed. Traceback:
  File "<python-input>", line 1, in <module>
    current_dt = apis.phone.get_current_date_and_time(access_token=phone_token)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Exception: Unexpected parameter 'access_token' passed to the get_current_date_and_time API of the phone app. Allowed parameters are: []
```


### Environment Interaction 10
----------------------------------------------------------------------------
```python

```

```
No code available to execute.
```


### Environment Interaction 11
----------------------------------------------------------------------------
```python
current_dt = apis.phone.get_current_date_and_time()
print(current_dt)
messages = apis.phone.search_text_messages(access_token=phone_token, phone_number='6017026518', page_index=0, page_limit=20, sort_by='-created_at')
print(messages)
```

```
{"date": "Thursday, May 18, 2023", "time": "12:00 PM"}
[
 {
  "text_message_id": 16807,
  "sender": {
   "contact_id": null,
   "name": "Matthew Blackburn",
   "phone_number": "4886643554"
  },
  "receiver": {
   "contact_id": 824,
   "name": "Kristin White",
   "phone_number": "6017026518"
  },
  "message": "sounds good.",
  "sent_at": "2023-05-18T18:30:17"
 },
 {
  "text_message_id": 16806,
  "sender": {
   "contact_id": 824,
   "name": "Kristin White",
   "phone_number": "6017026518"
  },
  "receiver": {
   "contact_id": null,
   "name": "Matthew Blackburn",
   "phone_number": "4886643554"
  },
  "message": "Oh right, how about you pay this time, and we'll call it even?",
  "sent_at": "2023-05-18T18:20:42"
 },
 {
  "text_message_id": 16803,
  "sender": {
   "contact_id": null,
   "name": "Matthew Blackburn",
   "phone_number": "4886643554"
  },
  "receiver": {
   "contact_id": 824,
   "name": "Kristin White",
   "phone_number": "6017026518"
  },
  "message": "sure, let's do it. That reminds me I owe you $25 from the last time.",
  "sent_at": "2023-05-18T18:15:00"
 },
 {
  "text_message_id": 16802,
  "sender": {
   "contact_id": 824,
   "name": "Kristin White",
   "phone_number": "6017026518"
  },
  "receiver": {
   "contact_id": null,
   "name": "Matthew Blackburn",
   "phone_number": "4886643554"
  },
  "message": "how about we go to watch a movie next weekend?",
  "sent_at": "2023-05-18T18:10:00"
 },
 {
  "text_message_id": 16800,
  "sender": {
   "contact_id": 824,
   "name": "Kristin White",
   "phone_number": "6017026518"
  },
  "receiver": {
   "contact_id": null,
   "name": "Matthew Blackburn",
   "phone_number": "4886643554"
  },
  "message": "great, thanks!",
  "sent_at": "2023-05-17T13:27:35"
 },
 {
  "text_message_id": 16797,
  "sender": {
   "contact_id": null,
   "name": "Matthew Blackburn",
   "phone_number": "4886643554"
  },
  "receiver": {
   "contact_id": 824,
   "name": "Kristin White",
   "phone_number": "6017026518"
  },
  "message": "cool, I'll send it to you on venmo.",
  "sent_at": "2023-05-17T13:26:32"
 },
 {
  "text_message_id": 16796,
  "sender": {
   "contact_id": 824,
   "name": "Kristin White",
   "phone_number": "6017026518"
  },
  "receiver": {
   "contact_id": null,
   "name": "Matthew Blackburn",
   "phone_number": "4886643554"
  },
  "message": "It was $54.",
  "sent_at": "2023-05-17T13:18:03"
 },
 {
  "text_message_id": 16793,
  "sender": {
   "contact_id": null,
   "name": "Matthew Blackburn",
   "phone_number": "4886643554"
  },
  "receiver": {
   "contact_id": 824,
   "name": "Kristin White",
   "phone_number": "6017026518"
  },
  "message": "hey, how much was yesterday's grocery?",
  "sent_at": "2023-05-17T13:17:11"
 },
 {
  "text_message_id": 6275,
  "sender": {
   "contact_id": null,
   "name": "Matthew Blackburn",
   "phone_number": "4886643554"
  },
  "receiver": {
   "contact_id": 824,
   "name": "Kristin White",
   "phone_number": "6017026518"
  },
  "message": "Thanks a bunch! Sending you warm wishes for a festive and joyful Christmas.",
  "sent_at": "2022-12-25T14:52:16"
 },
 {
  "text_message_id": 6274,
  "sender": {
   "contact_id": 824,
   "name": "Kristin White",
   "phone_number": "6017026518"
  },
  "receiver": {
   "contact_id": null,
   "name": "Matthew Blackburn",
   "phone_number": "4886643554"
  },
  "message": "Merry Christmas! May your days be merry and bright, and your heart be filled with holiday cheer.",
  "sent_at": "2022-12-25T14:51:06"
 },
 {
  "text_message_id": 4274,
  "sender": {
   "contact_id": 824,
   "name": "Kristin White",
   "phone_number": "6017026518"
  },
  "receiver": {
   "contact_id": null,
   "name": "Matthew Blackburn",
   "phone_number": "4886643554"
  },
  "message": "Thanks a bunch! Sending you warm wishes for a festive and joyful Christmas.",
  "sent_at": "2022-12-25T10:51:34"
 },
 {
  "text_message_id": 4271,
  "sender": {
   "contact_id": null,
   "name": "Matthew Blackburn",
   "phone_number": "4886643554"
  },
  "receiver": {
   "contact_id": 824,
   "name": "Kristin White",
   "phone_number": "6017026518"
  },
  "message": "Merry Christmas! May your days be merry and bright, and your heart be filled with holiday cheer.",
  "sent_at": "2022-12-25T10:26:04"
 }
]
```


### Environment Interaction 12
----------------------------------------------------------------------------
```python
print(apis.api_docs.show_api_doc(app_name='venmo', api_name='search_users'))
print(apis.api_docs.show_api_doc(app_name='venmo', api_name='create_transaction'))
```

```
{
 "app_name": "venmo",
 "api_name": "search_users",
 "path": "/venmo/users",
 "method": "GET",
 "description": "Search Venmo users by name or email address.",
 "parameters": [
  {
   "name": "access_token",
   "type": "string",
   "required": true,
   "description": "Access token obtained from venmo app login.",
   "default": null,
   "constraints": []
  },
  {
   "name": "query",
   "type": "string",
   "required": false,
   "description": "Search query string.",
   "default": "",
   "constraints": []
  },
  {
   "name": "page_index",
   "type": "integer",
   "required": false,
   "description": "The index of the page to return.",
   "default": 0,
   "constraints": [
    "value >= 0"
   ]
  },
  {
   "name": "page_limit",
   "type": "integer",
   "required": false,
   "description": "The maximum number of results to return per page.",
   "default": 5,
   "constraints": [
    "value >= 1, <= 20"
   ]
  }
 ],
 "response_schemas": {
  "success": [
   {
    "first_name": "string",
    "last_name": "string",
    "email": "user@example.com",
    "registered_at": "2019-01-01T00:00:00",
    "friends_since": "2019-01-01T00:00:00"
   }
  ],
  "failure": {
   "message": "string"
  }
 }
}
{
 "app_name": "venmo",
 "api_name": "create_transaction",
 "path": "/venmo/transactions",
 "method": "POST",
 "description": "Send money to a user.",
 "parameters": [
  {
   "name": "receiver_email",
   "type": "string",
   "required": true,
   "description": "Email address of the receiver.",
   "default": null,
   "constraints": [
    "value is email address"
   ]
  },
  {
   "name": "amount",
   "type": "number",
   "required": true,
   "description": "Amount of the transaction.",
   "default": null,
   "constraints": [
    "value > 0.0"
   ]
  },
  {
   "name": "access_token",
   "type": "string",
   "required": true,
   "description": "Access token obtained from venmo app login.",
   "default": null,
   "constraints": []
  },
  {
   "name": "description",
   "type": "string",
   "required": false,
   "description": "Description of or note about the transaction.",
   "default": "",
   "constraints": []
  },
  {
   "name": "payment_card_id",
   "type": "integer",
   "required": false,
   "description": "ID of the payment card to use for the transaction. If not passed, Venmo balance will be used.",
   "default": null,
   "constraints": []
  },
  {
   "name": "private",
   "type": "boolean",
   "required": false,
   "description": "Whether the transaction is private or not.",
   "default": false,
   "constraints": []
  }
 ],
 "response_schemas": {
  "success": {
   "message": "string",
   "transaction_id": 1
  },
  "failure": {
   "message": "string"
  }
 }
}
```


### Environment Interaction 13
----------------------------------------------------------------------------
```python
venmo_users = apis.venmo.search_users(access_token=venmo_token, query='Kristin White', page_limit=20)
print(venmo_users)
```

```
[
 {
  "first_name": "Kristin",
  "last_name": "White",
  "email": "kri-powe@gmail.com",
  "registered_at": "2022-12-17T11:05:29",
  "friends_since": "2022-12-17T11:05:29"
 },
 {
  "first_name": "Sierra",
  "last_name": "White",
  "email": "siwhit@gmail.com",
  "registered_at": "2022-07-24T18:43:41",
  "friends_since": "2022-07-24T18:43:41"
 },
 {
  "first_name": "Alex",
  "last_name": "White",
  "email": "alexwhite@gmail.com",
  "registered_at": "2023-01-17T16:28:47",
  "friends_since": null
 },
 {
  "first_name": "Timothy",
  "last_name": "White",
  "email": "timothy.whit@gmail.com",
  "registered_at": "2022-10-03T15:32:20",
  "friends_since": null
 },
 {
  "first_name": "Stephen",
  "last_name": "Mccoy",
  "email": "stmcco@gmail.com",
  "registered_at": "2023-01-24T12:51:50",
  "friends_since": null
 },
 {
  "first_name": "Laura",
  "last_name": "Mccoy",
  "email": "la-mcco@gmail.com",
  "registered_at": "2023-02-12T14:30:46",
  "friends_since": null
 },
 {
  "first_name": "Chris",
  "last_name": "Mccoy",
  "email": "chris.mcco@gmail.com",
  "registered_at": "2022-08-25T08:57:40",
  "friends_since": null
 },
 {
  "first_name": "Jonathan",
  "last_name": "Ball",
  "email": "jo.ball@gmail.com",
  "registered_at": "2022-08-26T16:01:41",
  "friends_since": null
 },
 {
  "first_name": "Leslie",
  "last_name": "Ball",
  "email": "les_ball@gmail.com",
  "registered_at": "2023-02-08T08:46:59",
  "friends_since": null
 },
 {
  "first_name": "Bradley",
  "last_name": "Ball",
  "email": "bradley_ball@gmail.com",
  "registered_at": "2022-04-27T18:22:21",
  "friends_since": null
 },
 {
  "first_name": "Katherine",
  "last_name": "Smith",
  "email": "ka_ball@gmail.com",
  "registered_at": "2022-04-25T18:24:54",
  "friends_since": null
 },
 {
  "first_name": "Thomas",
  "last_name": "Solomon",
  "email": "thomas.solomon@gmail.com",
  "registered_at": "2022-05-09T14:11:52",
  "friends_since": null
 },
 {
  "first_name": "Jamie",
  "last_name": "Solomon",
  "email": "jamie-solomon@gmail.com",
  "registered_at": "2023-01-17T09:00:50",
  "friends_since": null
 },
 {
  "first_name": "James",
  "last_name": "Solomon",
  "email": "ja-solomon@gmail.com",
  "registered_at": "2022-10-02T15:33:08",
  "friends_since": null
 },
 {
  "first_name": "Troy",
  "last_name": "Solomon",
  "email": "tr_solo@gmail.com",
  "registered_at": "2022-04-05T09:14:55",
  "friends_since": null
 },
 {
  "first_name": "Ronald",
  "last_name": "Harrison",
  "email": "ron.harrison@gmail.com",
  "registered_at": "2022-07-28T16:36:46",
  "friends_since": null
 },
 {
  "first_name": "Christina",
  "last_name": "Harrison",
  "email": "chrharrison@gmail.com",
  "registered_at": "2022-10-01T16:49:36",
  "friends_since": null
 },
 {
  "first_name": "Jose",
  "last_name": "Harrison",
  "email": "joseharr@gmail.com",
  "registered_at": "2022-12-14T14:46:35",
  "friends_since": null
 },
 {
  "first_name": "Jordan",
  "last_name": "Harrison",
  "email": "jo-harr@gmail.com",
  "registered_at": "2022-04-10T14:26:20",
  "friends_since": null
 },
 {
  "first_name": "Anthony",
  "last_name": "Harrison",
  "email": "an-harrison@gmail.com",
  "registered_at": "2022-12-23T16:09:19",
  "friends_since": "2022-12-23T16:09:19"
 }
]
```


### Environment Interaction 14
----------------------------------------------------------------------------
```python
result = apis.venmo.create_transaction(access_token=venmo_token, receiver_email='kri-powe@gmail.com', amount=54, description='Groceries')
print(result)
```

```
{"message": "Sent money.", "transaction_id": 8216}
```


### Environment Interaction 15
----------------------------------------------------------------------------
```python
print(apis.api_docs.show_api_doc(app_name='phone', api_name='send_text_message'))
```

```
{
 "app_name": "phone",
 "api_name": "send_text_message",
 "path": "/phone/messages/text/{phone_number}",
 "method": "POST",
 "description": "Send a text message on the given phone number.",
 "parameters": [
  {
   "name": "phone_number",
   "type": "string",
   "required": true,
   "description": "The phone number of the contact to send the message to.",
   "default": null,
   "constraints": []
  },
  {
   "name": "message",
   "type": "string",
   "required": true,
   "description": "The content of the text message.",
   "default": null,
   "constraints": [
    "length >= 1"
   ]
  },
  {
   "name": "access_token",
   "type": "string",
   "required": true,
   "description": "Access token obtained from phone app login.",
   "default": null,
   "constraints": []
  }
 ],
 "response_schemas": {
  "success": {
   "message": "string",
   "text_message_id": 1
  },
  "failure": {
   "message": "string"
  }
 }
}
```


### Environment Interaction 16
----------------------------------------------------------------------------
```python
msg_result = apis.phone.send_text_message(phone_number='6017026518', message='It is done.', access_token=phone_token)
print(msg_result)
```

```
{"message": "Text message sent.", "text_message_id": 16809}
```


### Environment Interaction 17
----------------------------------------------------------------------------
```python
apis.supervisor.complete_task()
```

```
Execution successful.
```

