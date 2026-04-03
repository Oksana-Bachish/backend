from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView, UpdateView, TemplateView
from django.db.models import Prefetch
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from baskets.models import Basket
from common.mixins import CacheMixin
from orders.models import Order, OrderItem
from users.forms import UserLoginForm, UserRegistrationForm, ProfileForm


class UserLoginView(LoginView):
    template_name = 'users/login.html'
    form_class = UserLoginForm

    def get_success_url(self):
        redirect_page = self.request.POST.get('next', None)
        if redirect_page and redirect_page != reverse_lazy('users:logout'):
            return redirect_page
        return reverse_lazy('main:index')

    def form_valid(self, form):
        session_key = self.request.session.session_key
        user = form.get_user()
        if user:
            auth.login(self.request, user)
            if session_key:
                Basket.objects.filter(user=user).delete()
                Basket.objects.filter(session_key=session_key).update(user=user)
            messages.success(self.request, f'{user.username}, Вы вошли в аккаунт')
            return HttpResponseRedirect(self.get_success_url())
        return super(UserLoginView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Electronics_store - Авторизация'
        return context


class UserRegistrationView(CreateView):
    template_name = 'users/registration.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('users:profile')

    def form_valid(self, form):
        session_key = self.request.session.session_key
        user = form.instance

        if user:
            form.save()
            auth.login(self.request, user)

        if session_key:
            Basket.objects.filter(session_key=session_key).update(user=user)

        messages.success(self.request, f'{user.username}, Вы успешно зарегистрированы и вошли в аккаунт')
        return HttpResponseRedirect(self.success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Electronics_store - Регистрация'
        return context


class UserProfileView(LoginRequiredMixin, UpdateView):
    template_name = 'users/profile.html'
    form_class = ProfileForm
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Профайл успешно обновлен")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Произошла ошибка')
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Electronics_store - Кабинет'
        orders = Order.objects.filter(user=self.request.user).prefetch_related(Prefetch('orderitem_set', queryset=OrderItem.objects.select_related('product'))).order_by('-id')
        context['orders'] = orders
        return context


class UsersCartView(TemplateView):
    template_name = 'users/users_basket.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Electronics_store - Корзина'
        return context


@login_required
def logout(request):
    messages.success(request, f"{request.user.username}, Вы вышли из аккаунта")
    auth.logout(request)
    return redirect(reverse('main:index'))


# Функциональные представления

# def login(request):
#     if request.method == 'POST':
#         form = UserLoginForm(data=request.POST)
#         if form.is_valid():
#             username = request.POST['username']
#             password = request.POST['password']
#             user = auth.authenticate(username=username, password=password)
#
#             session_key = request.session.session_key  # пполучаем сессионный ключ
#
#             if user:
#                 auth.login(request, user)
#                 messages.success(request, f'{username}, Вы вошли в аккаунт')
#
#                 if session_key:
#                     forgot_carts = Basket.objects.filter(user=user)
#                     if forgot_carts.exists():
#                         forgot_carts.delete()
#                     Basket.objects.filter(session_key=session_key).update(user=user)
#
#                 redirect_page = request.POST.get('next', None)
#                 if redirect_page and redirect_page != reverse('users:logout'):
#                     return HttpResponseRedirect(
#                         request.POST.get('next'))  # входим на страницу, которую посещали до входа в аккаунт
#                 return HttpResponseRedirect(reverse('main:index'))
#     else:
#         form = UserLoginForm()
#
#     context = {
#         'title': 'Electronics_store - Авторизуйтесь',
#         'form': form,
#     }
#     return render(request, 'users/login.html', context)


# def registration(request):
#     if request.method == 'POST':
#         form = UserRegistrationForm(data=request.POST)
#         if form.is_valid():
#             form.save()
#
#             session_key = request.session.session_key
#
#             user = form.instance
#             auth.login(request, user)
#
#             if session_key:
#                 Basket.objects.filter(session_key=session_key).update(user=user)
#
#             messages.success(request, f'{user.username}, Вы успешно зарегистрированы и вошли в аккаунт')
#             return HttpResponseRedirect(reverse('main:index'))
#     else:
#         form = UserRegistrationForm()
#
#     context = {
#         'title': 'Electronics_store - Регистрация',
#         'form': form,
#     }
#     return render(request, 'users/registration.html', context)


# @login_required
# def profile(request):
#     if request.method == 'POST':
#         form = ProfileForm(data=request.POST, instance=request.user, files=request.FILES)
#         if form.is_valid():
#             form.save()
#             messages.success(request, "Профайл успешно создан")
#             return HttpResponseRedirect(reverse('users:profile'))
#     else:
#         form = ProfileForm(instance=request.user)
#
#     orders = (
#         Order.objects.filter(user=request.user).prefetch_related(Prefetch('orderitem_set', queryset=OrderItem.objects.select_related('product'))).order_by('-id'))
#     # prefetch_related - «жадная» загрузка связанных данных по внешнему ключу key, который имеет тип ManyToManyField. 'orederitem_set' - имя дополнительного query set
#     context = {
#         'title': 'Electronics_store - Кабинет',
#         'form': form,
#         'orders': orders,
#     }
#     return render(request, 'users/profile.html', context)
#
# def users_cart(request):
#     return render(request, 'users/users_basket.html')