from django.db import models


class AppliedCandidates(models.Model):
    post = models.ForeignKey('post.Post', on_delete=models.CASCADE)
    user = models.ForeignKey('users.UserAccount', on_delete=models.CASCADE)
    profile = models.ForeignKey('users.UserProfile', on_delete=models.CASCADE)
    cv = models.FileField(upload_to='cvs/', null=True, blank=True)

    status = models.CharField(max_length=20, default='Pending')

    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['post', 'user']

    def __str__(self):
        return f"{self.user} applied for {self.post}"
