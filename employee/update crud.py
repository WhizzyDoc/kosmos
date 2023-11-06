class BankAccountRetrieveView(RetrieveAPIView):
    serializer_class = BankAccountSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user = Profile.objects.get(api_key=self.request.data['api_key'])
        return BankAccount.objects.filter(user=user)

class BankAccountUpdateView(UpdateAPIView):
    serializer_class = BankAccountSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        # Retrieve the user based on the "api_token" from the URL
        api_token = self.kwargs.get('pk')
        user = Profile.objects.get(api_token=api_token)

        # Retrieve the specific BankAccount object for the user
        bank_account_id = self.kwargs.get('pk')
        return BankAccount.objects.filter(user=user, id=bank_account_id)

    def update(self, request, *args, **kwargs):
        # Retrieve the BankAccount object to update
        instance = self.get_object()

        # Make sure the user and bank are not updated in the request data
        request.data.pop('user', None)
        request.data.pop('bank', None)

        serializer = self.get_serializer(instance, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BankAccountDeleteView(DestroyAPIView):
    serializer_class = BankAccountSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user = Profile.objects.get(api_key=self.request.data['api_key'])
        return BankAccount.objects.filter(user=user)
