from background_task import background

@background(schedule=60)
def notify_user():
    # lookup user by id and send them a message
    print("I ran!")