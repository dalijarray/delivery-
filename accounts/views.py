from django.http import JsonResponse
from django.shortcuts import render, redirect
from .forms import SignupForm
from .models import CustomUser, Order, Product, ProductImage
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
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

def admin_dashboard(request):
    if request.user.role != 'admin':
        return redirect('login')

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        image = request.FILES.get('image')  # Image principale
        extra_images = request.FILES.getlist('extra_images')  # Images supplémentaires

        # Validation
        if not all([name, description, price, stock]):
            return render(request, 'accounts/admin_dashboard.html', {
                'error': 'Tous les champs sont requis.'
            })

        try:
            product = Product(
                name=name,
                description=description,
                price=price,
                stock=stock,
                image=image
            )
            product.save()

            # Ajout des images supplémentaires
            for img in extra_images:
                ProductImage.objects.create(product=product, image=img)

            return render(request, 'accounts/admin_dashboard.html', {
                'success': 'Produit ajouté avec succès !'
            })
        except Exception as e:
            return render(request, 'accounts/admin_dashboard.html', {
                'error': f'Erreur lors de l’ajout : {str(e)}'
            })

    return render(request, 'accounts/admin_dashboard.html')

def livreur_dashboard(request):
    if request.user.role != 'livreur':
        return redirect('login')
    return render(request, 'accounts/livreur_dashboard.html')

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

            if payment_method == 'card':
                # Redirect to payment processing for card payments
                return redirect('process_payment', product_id=product_id)
            else:
                # Handle cash payment
                order = Order(
                    client=request.user,
                    product=product,
                    quantity=quantity,
                    payment_method=payment_method,
                    location=location,
                    total_price=product.price * int(quantity),
                )
                order.save()

                product.stock -= int(quantity)
                product.save()

                # Redirect to orders page
                return redirect('orders')

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
    

@login_required
def orders(request):
    if request.user.role != 'client':
        return redirect('login')

    orders = Order.objects.filter(client=request.user).order_by('-created_at')
    return render(request, 'accounts/orders.html', {'orders': orders})