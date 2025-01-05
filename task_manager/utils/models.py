from tortoise import fields, models

class Task(models.Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length = 50)
    description = fields.CharField(max_length = 200,null = True)
    status = fields.CharField(max_length = 20,default = "pending")

def __str__(self):
    return f"Task id : {self.id}\n title : {self.title}\n description : {self.description}\n status : {self.status}"



