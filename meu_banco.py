menu = '''
[d] Depositar
[s] Sacar
[e] Extrato
[q] Sair
=> '''

saldo = 0
limite = 500
sacou = 0
valor_depositado = 0
soma_saque = 0
soma_depositado = 0
valores_sacados = []
valores_depositados = []
continuar_opcao = True
NUMEROS_DE_SAQUES = 3

while continuar_opcao:
    opcao = input(menu)
    if opcao == "d":
        valor_depositado = int(input("Digite o valor a ser depositado: R$"))
        if valor_depositado <= 0:
            print("Valor inválido! \n Tente novamente com um valor acima de 0.")
        else:
            print(f"Você depositou R${valor_depositado}")
            valores_depositados.append(valor_depositado)
            saldo+= valor_depositado
 
    elif opcao == "s":
        if sacou >= NUMEROS_DE_SAQUES:
            print("Você atingiu o limite de saques diário(3), dentro de 24 horas você poderá sacar novamente!")
        else:
            valor_a_sacar = int(input("Digite o valor para sacar: R$"))
            if valor_a_sacar > limite:
                print(f"O valor limite por saque é de R${limite} \n Solicite um valor menor de saque!")
            elif valor_a_sacar > saldo:
                print(f"Você não tem saldo suficiente para esse saque! \n Seu saldo atual é de R${saldo}")
            else:
                print(f"Transação autorizada! \n Você sacou R${valor_a_sacar}")
                saldo -= valor_a_sacar
                sacou +=1
                valores_sacados.append(valor_a_sacar)

        for valor in valores_depositados:
            soma_depositado += valor
        
        for valor_2 in valores_sacados:
            soma_saque += valor_2

    elif opcao == "e":
        print(f"Você sacou {sacou} vez(es) nas últimas 24 horas, totalizando R${soma_saque}")
        print(f"Você realizou {len(valores_depositados)} depósitos nas últimas 24 horas num valor total de R${soma_depositado}")
        print(f"O seu saldo atual é de R${saldo}")

    elif opcao == "q":
        print("Operação Finalizada!")
        continuar_opcao = False

    else:
        print("Opção inválida!! \n Tente novamente.")

    continuar = str(input("Deseja realizar uma nova operação? [S]/[N]: ")).lower()
    if continuar == 's':
        continuar_opcao = True
    else:
        continuar_opcao = False 
print(soma_depositado)
print(soma_saque)