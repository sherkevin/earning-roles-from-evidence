
### Environment Interaction 1
----------------------------------------------------------------------------
```python
print(apis.api_docs.show_api_descriptions(app_name='phone'))
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
```


### Environment Interaction 2
----------------------------------------------------------------------------
```python
print(apis.api_docs.show_api_doc(app_name='phone', api_name='search_contacts'))
```

```
{
 "app_name": "phone",
 "api_name": "search_contacts",
 "path": "/phone/contacts",
 "method": "GET",
 "description": "Search your contact book for relatives' information.",
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
   "description": "Search query for the contacts list.",
   "default": "",
   "constraints": []
  },
  {
   "name": "relationship",
   "type": "string",
   "required": false,
   "description": "Relationship with the person in the contacts list to filter by.",
   "default": null,
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
    "contact_id": 1,
    "first_name": "string",
    "last_name": "string",
    "email": "user@example.com",
    "phone_number": "string",
    "relationships": [
     "string"
    ],
    "birthday": "string",
    "home_address": "string",
    "work_address": "string",
    "created_at": "2019-01-01T00:00:00"
   }
  ],
  "failure": {
   "message": "string"
  }
 }
}
```


### Environment Interaction 3
----------------------------------------------------------------------------
```python
print(apis.api_docs.show_api_doc(app_name='supervisor', api_name='show_account_passwords'))
```

```
{
 "app_name": "supervisor",
 "api_name": "show_account_passwords",
 "path": "/supervisor/account_passwords",
 "method": "GET",
 "description": "Show your supervisor's app account passwords.",
 "parameters": [],
 "response_schemas": {
  "success": [
   {
    "account_name": "string",
    "password": "string"
   }
  ],
  "failure": {
   "message": "string"
  }
 }
}
```


### Environment Interaction 4
----------------------------------------------------------------------------
```python
print(apis.api_docs.show_api_doc(app_name='phone', api_name='login'))
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
```


### Environment Interaction 5
----------------------------------------------------------------------------
```python
passwords = apis.supervisor.show_account_passwords()
print(passwords)
```

```
[
 {
  "account_name": "amazon",
  "password": "#nMYk-D"
 },
 {
  "account_name": "file_system",
  "password": "]QxW}_v"
 },
 {
  "account_name": "gmail",
  "password": "BJTw{yJ"
 },
 {
  "account_name": "phone",
  "password": "X^1PnVS"
 },
 {
  "account_name": "simple_note",
  "password": "e23T0l4"
 },
 {
  "account_name": "splitwise",
  "password": "pdIg#$L"
 },
 {
  "account_name": "spotify",
  "password": "-m^8gsb"
 },
 {
  "account_name": "todoist",
  "password": "]Dyolbq"
 },
 {
  "account_name": "venmo",
  "password": "O*3)aho"
 }
]
```


### Environment Interaction 6
----------------------------------------------------------------------------
```python
phone_password = next(item['password'] for item in passwords if item['account_name'] == 'phone')
phone_login = apis.phone.login(username='8903665635', password=phone_password)
print(phone_login)
```

```
{
 "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJwaG9uZSs4OTAzNjY1NjM1IiwiZXhwIjoxNjg0NDEyMDU4fQ.Fo_DXcCEfknwhsBdZGJzNx-sYoBsL3E48J1EUV1DsIs",
 "token_type": "Bearer"
}
```


### Environment Interaction 7
----------------------------------------------------------------------------
```python
phone_access_token = phone_login['access_token']
joseph_contacts = apis.phone.search_contacts(access_token=phone_access_token, query='Joseph')
print(joseph_contacts)
```

```
[
 {
  "contact_id": 327,
  "first_name": "Joseph",
  "last_name": "Weber",
  "email": "joseph.webe@gmail.com",
  "phone_number": "2233697879",
  "relationships": [
   "friend"
  ],
  "birthday": "1996-09-29",
  "home_address": "28073 William Corners Suite 495\nSeattle\nWashington\nUnited States\n36752",
  "work_address": "96967 Fox Loop Suite 397\nSeattle\nWashington\nUnited States\n86832",
  "created_at": "2023-04-15T06:00:06"
 },
 {
  "contact_id": 320,
  "first_name": "Adrian",
  "last_name": "Burton",
  "email": "adrian_burt@gmail.com",
  "phone_number": "5025534184",
  "relationships": [
   "partner",
   "husband"
  ],
  "birthday": "1991-06-10",
  "home_address": "5754 Kaylee Trace Suite 282\nSeattle\nWashington\nUnited States\n18299",
  "work_address": "97051 Keith Spur Suite 381\nSeattle\nWashington\nUnited States\n29218",
  "created_at": "2023-04-15T06:00:06"
 },
 {
  "contact_id": 321,
  "first_name": "Jose",
  "last_name": "Harrison",
  "email": "joseharr@gmail.com",
  "phone_number": "2474975253",
  "relationships": [
   "sibling",
   "brother"
  ],
  "birthday": "1985-12-15",
  "home_address": "172 Matthew Knolls Suite 730\nSeattle\nWashington\nUnited States\n65644",
  "work_address": "774 Samuel Cape Suite 202\nSeattle\nWashington\nUnited States\n16844",
  "created_at": "2023-04-15T06:00:06"
 },
 {
  "contact_id": 322,
  "first_name": "Jordan",
  "last_name": "Harrison",
  "email": "jo-harr@gmail.com",
  "phone_number": "2254213734",
  "relationships": [
   "sibling",
   "brother"
  ],
  "birthday": "1988-04-06",
  "home_address": "4912 Morales Divide Suite 845\nSeattle\nWashington\nUnited States\n24529",
  "work_address": "8875 Amy Extensions Suite 797\nSeattle\nWashington\nUnited States\n49596",
  "created_at": "2023-04-15T06:00:06"
 },
 {
  "contact_id": 323,
  "first_name": "Anthony",
  "last_name": "Harrison",
  "email": "an-harrison@gmail.com",
  "phone_number": "2466064078",
  "relationships": [
   "sibling",
   "brother"
  ],
  "birthday": "1990-06-09",
  "home_address": "247 Salinas Pines Suite 668\nSeattle\nWashington\nUnited States\n11799",
  "work_address": "96967 Fox Loop Suite 397\nSeattle\nWashington\nUnited States\n86832",
  "created_at": "2023-04-15T06:00:06"
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
joseph_phone = '2233697879'
joseph_messages = []
page_index = 0
while True:
    page = apis.phone.search_text_messages(access_token=phone_access_token, phone_number=joseph_phone, page_index=page_index, page_limit=20)
    if not page:
        break
    joseph_messages.extend(page)
    if len(page) < 20:
        break
    page_index += 1
print(len(joseph_messages))
for m in joseph_messages:
    print(m)
```

```
11
{
 "text_message_id": 16807,
 "sender": {
  "contact_id": null,
  "name": "Morgan Burton",
  "phone_number": "8903665635"
 },
 "receiver": {
  "contact_id": 327,
  "name": "Joseph Weber",
  "phone_number": "2233697879"
 },
 "message": "sounds good.",
 "sent_at": "2023-05-18T17:39:20"
}
{
 "text_message_id": 16806,
 "sender": {
  "contact_id": 327,
  "name": "Joseph Weber",
  "phone_number": "2233697879"
 },
 "receiver": {
  "contact_id": null,
  "name": "Morgan Burton",
  "phone_number": "8903665635"
 },
 "message": "Oh right, how about you pay this time, and we'll call it even?",
 "sent_at": "2023-05-18T17:29:43"
}
{
 "text_message_id": 16803,
 "sender": {
  "contact_id": null,
  "name": "Morgan Burton",
  "phone_number": "8903665635"
 },
 "receiver": {
  "contact_id": 327,
  "name": "Joseph Weber",
  "phone_number": "2233697879"
 },
 "message": "sure, let's do it. That reminds me I owe you $37 from the last time.",
 "sent_at": "2023-05-18T17:24:40"
}
{
 "text_message_id": 16802,
 "sender": {
  "contact_id": 327,
  "name": "Joseph Weber",
  "phone_number": "2233697879"
 },
 "receiver": {
  "contact_id": null,
  "name": "Morgan Burton",
  "phone_number": "8903665635"
 },
 "message": "how about we go to watch a movie next weekend?",
 "sent_at": "2023-05-18T17:19:01"
}
{
 "text_message_id": 16800,
 "sender": {
  "contact_id": 327,
  "name": "Joseph Weber",
  "phone_number": "2233697879"
 },
 "receiver": {
  "contact_id": null,
  "name": "Morgan Burton",
  "phone_number": "8903665635"
 },
 "message": "great, thanks!",
 "sent_at": "2023-05-17T16:56:33"
}
{
 "text_message_id": 16797,
 "sender": {
  "contact_id": null,
  "name": "Morgan Burton",
  "phone_number": "8903665635"
 },
 "receiver": {
  "contact_id": 327,
  "name": "Joseph Weber",
  "phone_number": "2233697879"
 },
 "message": "cool, I'll send it to you on venmo.",
 "sent_at": "2023-05-17T16:54:23"
}
{
 "text_message_id": 16796,
 "sender": {
  "contact_id": 327,
  "name": "Joseph Weber",
  "phone_number": "2233697879"
 },
 "receiver": {
  "contact_id": null,
  "name": "Morgan Burton",
  "phone_number": "8903665635"
 },
 "message": "It was $98.",
 "sent_at": "2023-05-17T16:45:21"
}
{
 "text_message_id": 16793,
 "sender": {
  "contact_id": null,
  "name": "Morgan Burton",
  "phone_number": "8903665635"
 },
 "receiver": {
  "contact_id": 327,
  "name": "Joseph Weber",
  "phone_number": "2233697879"
 },
 "message": "hey, how much was yesterday's grocery?",
 "sent_at": "2023-05-17T16:43:36"
}
{
 "text_message_id": 2448,
 "sender": {
  "contact_id": 327,
  "name": "Joseph Weber",
  "phone_number": "2233697879"
 },
 "receiver": {
  "contact_id": null,
  "name": "Morgan Burton",
  "phone_number": "8903665635"
 },
 "message": "No worries. See you next time.",
 "sent_at": "2023-01-29T10:56:33"
}
{
 "text_message_id": 2445,
 "sender": {
  "contact_id": null,
  "name": "Morgan Burton",
  "phone_number": "8903665635"
 },
 "receiver": {
  "contact_id": 327,
  "name": "Joseph Weber",
  "phone_number": "2233697879"
 },
 "message": "Sorry, I have plans already. Maybe next time.",
 "sent_at": "2023-01-29T10:10:03"
}
{
 "text_message_id": 2444,
 "sender": {
  "contact_id": 327,
  "name": "Joseph Weber",
  "phone_number": "2233697879"
 },
 "receiver": {
  "contact_id": null,
  "name": "Morgan Burton",
  "phone_number": "8903665635"
 },
 "message": "Hey, I am hosting a game night at my place this Friday. Would be great if you can join! Let me know.",
 "sent_at": "2023-01-29T09:33:17"
}
```


### Environment Interaction 10
----------------------------------------------------------------------------
```python
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


### Environment Interaction 11
----------------------------------------------------------------------------
```python

```

```
No code available to execute.
```


### Environment Interaction 12
----------------------------------------------------------------------------
```python

```

```
No code available to execute.
```


### Environment Interaction 13
----------------------------------------------------------------------------
```python
print(apis.api_docs.show_api_doc(app_name='venmo', api_name='login'))
```

```
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


### Environment Interaction 14
----------------------------------------------------------------------------
```python
venmo_password = next(item['password'] for item in passwords if item['account_name'] == 'venmo')
venmo_login = apis.venmo.login(username='morgan-harrison@gmail.com', password=venmo_password)
print(venmo_login)
```

```
{
 "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ2ZW5tbyttb3JnYW4taGFycmlzb25AZ21haWwuY29tIiwiZXhwIjoxNjg0NDExOTA5fQ.hXac8ZXlFyMSFdqg_w8q-inmrNCw5IvDTYfWvkrNQwo",
 "token_type": "Bearer"
}
```


### Environment Interaction 15
----------------------------------------------------------------------------
```python
venmo_access_token = venmo_login['access_token']
print(apis.api_docs.show_api_doc(app_name='venmo', api_name='search_users'))
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
```


### Environment Interaction 16
----------------------------------------------------------------------------
```python
joseph_users = apis.venmo.search_users(access_token=venmo_access_token, query='Joseph Weber')
print(joseph_users)
```

```
[
 {
  "first_name": "Joseph",
  "last_name": "Weber",
  "email": "joseph.webe@gmail.com",
  "registered_at": "2023-02-18T10:55:16",
  "friends_since": "2023-02-18T10:55:16"
 },
 {
  "first_name": "Tracy",
  "last_name": "Weber",
  "email": "tra_weber@gmail.com",
  "registered_at": "2023-01-06T17:07:00",
  "friends_since": null
 },
 {
  "first_name": "Nicholas",
  "last_name": "Weber",
  "email": "nicholas.weber@gmail.com",
  "registered_at": "2022-03-24T17:16:25",
  "friends_since": null
 },
 {
  "first_name": "Miranda",
  "last_name": "Weber",
  "email": "mir-powe@gmail.com",
  "registered_at": "2022-08-14T08:39:56",
  "friends_since": null
 },
 {
  "first_name": "Brandon",
  "last_name": "Weber",
  "email": "brandon-webe@gmail.com",
  "registered_at": "2023-02-03T10:24:32",
  "friends_since": null
 }
]
```


### Environment Interaction 17
----------------------------------------------------------------------------
```python
print(apis.api_docs.show_api_doc(app_name='venmo', api_name='create_transaction'))
```

```
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


### Environment Interaction 18
----------------------------------------------------------------------------
```python
print(apis.venmo.show_venmo_balance(access_token=venmo_access_token))
```

```
{"venmo_balance": 10200.0}
```


### Environment Interaction 19
----------------------------------------------------------------------------
```python
transaction = apis.venmo.create_transaction(
    access_token=venmo_access_token,
    receiver_email='joseph.webe@gmail.com',
    amount=98.0,
    description='Grocery Bill'
)
print(transaction)
```

```
{"message": "Sent money.", "transaction_id": 8216}
```


### Environment Interaction 20
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


### Environment Interaction 21
----------------------------------------------------------------------------
```python
text_result = apis.phone.send_text_message(
    access_token=phone_access_token,
    phone_number='2233697879',
    message='Done.'
)
print(text_result)
```

```
{"message": "Text message sent.", "text_message_id": 16809}
```


### Environment Interaction 22
----------------------------------------------------------------------------
```python
apis.supervisor.complete_task()
```

```
Execution successful.
```

