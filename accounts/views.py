from django.http import JsonResponse
from django.shortcuts import render, redirect
from .forms import SignupForm
from .models import CustomUser, Order, Product, ProductImage
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password

# signup
def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        role = request.POST.get('role')

        # Vérifications
        if password != password_confirm:
            return render(request, 'accounts/signup.html', {'error': 'Les mots de passe ne correspondent pas'})
        if CustomUser.objects.filter(username=username).exists():
            return render(request, 'accounts/signup.html', {'error': 'Ce nom d’utilisateur est déjà pris'})
        if CustomUser.objects.filter(email=email).exists():
            return render(request, 'accounts/signup.html', {'error': 'Cet email est déjà utilisé'})

        # Création de l'utilisateur
        user = CustomUser(
            username=username,
            email=email,
            password=make_password(password),  # Hachage du mot de passe
            role=role
        )
        user.save()

        # Connexion automatique après inscription
        login(request, user)
        if user.role == 'admin':
            return redirect('admin_dashboard')
        elif user.role == 'livreur':
            return redirect('livreur_dashboard')
        else:
            return redirect('client_dashboard')
    
    # Si méthode GET, afficher le formulaire vide
    return render(request, 'accounts/signup.html')
# login
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirection en fonction du rôle
            if user.role == 'admin':
                return redirect('admin_dashboard')
            elif user.role == 'livreur':
                return redirect('livreur_dashboard')
            else:
                return redirect('client_dashboard')
        else:
            # Si l'authentification échoue, renvoyer une erreur
            return render(request, 'accounts/login.html', {'error': 'Nom d’utilisateur ou mot de passe incorrect'})
    # Si méthode GET, afficher le formulaire vide
    return render(request, 'accounts/login.html')

# logout
def user_logout(request):
    logout(request)
    return redirect('login')

# admin_dashboard
# admin_add_product
def admin_add_product(request):
    if request.user.role != 'admin':
        return redirect('login')

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        image = request.FILES.get('image')
        extra_images = request.FILES.getlist('extra_images')

        if not all([name, description, price, stock]):
            return render(request, 'accounts/admin_add_product.html', {'error': 'Tous les champs sont requis.'})

        try:
            product = Product(name=name, description=description, price=price, stock=stock, image=image)
            product.save()
            for img in extra_images:
                ProductImage.objects.create(product=product, image=img)
            return render(request, 'accounts/admin_add_product.html', {'success': 'Produit ajouté avec succès !'})
        except Exception as e:
            return render(request, 'accounts/admin_add_product.html', {'error': f'Erreur : {str(e)}'})

    return render(request, 'accounts/admin_add_product.html')

# admin_orders
def admin_orders(request):
    if request.user.role != 'admin':
        return redirect('login')

    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        livreur_id = request.POST.get('livreur_id')
        try:
            order = Order.objects.get(id=order_id)
            livreur = CustomUser.objects.get(id=livreur_id, role='livreur')
            order.livreur = livreur
            order.status = 'assigned'
            order.save()
            return render(request, 'accounts/admin_orders.html', {'success': f'Livreur affecté à la commande {order.id} !'})
        except Order.DoesNotExist:
            return render(request, 'accounts/admin_orders.html', {'error': 'Commande non trouvée.'})
        except CustomUser.DoesNotExist:
            return render(request, 'accounts/admin_orders.html', {'error': 'Livreur non trouvé.'})

    orders = Order.objects.all()
    livreurs = CustomUser.objects.filter(role='livreur')
    return render(request, 'accounts/admin_orders.html', {'orders': orders, 'livreurs': livreurs})

#livreur_dashboard
def livreur_dashboard(request):
    if request.user.role != 'livreur':
        return redirect('login')
    return render(request, 'accounts/livreur_dashboard.html')

# client_dashboard
def client_dashboard(request):
    if request.user.role != 'client':
        return redirect('login')

    products = Product.objects.all()

    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity', 1)
        payment_method = request.POST.get('payment_method')
        location = request.POST.get('location', 'Localisation non précisée')

        try:
            product = Product.objects.get(id=product_id)
            if product.stock < int(quantity):
                return render(request, 'accounts/client_dashboard.html', {
                    'products': products,
                    'error': f"Stock insuffisant pour {product.name} (disponible : {product.stock})"
                })

            order = Order(
                client=request.user,
                product=product,
                quantity=quantity,
                payment_method=payment_method,
                location=location
            )
            order.save()

            product.stock -= int(quantity)
            product.save()

            return render(request, 'accounts/client_dashboard.html', {
                'products': products,
                'success': f"Commande de {product.name} passée avec succès !"
            })
        except Product.DoesNotExist:
            return render(request, 'accounts/client_dashboard.html', {
                'products': products,
                'error': "Produit non trouvé."
            })

    return render(request, 'accounts/client_dashboard.html', {'products': products})

# Vue AJAX pour les détails du produit
def product_detail(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        images = product.images.all()  # Images supplémentaires
        data = {
            'name': product.name,
            'price': str(product.price),
            'description': product.description,
            'image': product.image.url if product.image else None,
            'extra_images': [img.image.url for img in images],
            'stock': product.stock
        }
        return JsonResponse(data)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Produit non trouvé'}, status=404)