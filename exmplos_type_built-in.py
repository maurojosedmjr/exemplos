classe_pessoa = type(
  "Pessoa",
  (),
  {
    "__init__": lambda self, name: setattr(self, "name", name),
    "to_dict": lambda self: {"nome": self.name},
    "repr": lambda self: f"Classe {self} - Nome: {self.name}",
  }
)
var_mauro = classe_pessoa("Mauro")
print(var_mauro) # <__main__.Pessoa at 0x7fee281c2d60>
var_mauro.name # 'Mauro'
var_mauro.to_dict() # {'nome': 'Mauro'}
var_mauro.repr() # 'Classe <__main__.Pessoa object at 0x7fee281d1dc0> - Nome: Mauro'
