# Notifications — User & Workflow Messaging

## Purpose
The notifications app provides in-product notifications for events requiring user awareness or action.

## Responsibilities
- Create tenant/user notifications.
- Track read/unread state.
- List notifications.
- Mark one or all notifications as read.
- Integrate with asynchronous workflow events.

## Architecture
Domain event → notification service/task → Notification → frontend notification center.

Notifications are derived communication records, not the authoritative source of workflow state.

## Security design
A user can only read or mutate notifications addressed to that user and inside the authorized tenant.

## Testing
Cover recipient isolation, tenant isolation, unread counts, read transitions and duplicate event handling.

## Design invariant
Notifications tell users what needs attention; domain records remain the source of truth.
