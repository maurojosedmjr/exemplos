from pydantic import BaseModel, Field, ValidationError
from typing import Dict, List, Optional, Any, Union
import copy
import json


class PropertySchema(BaseModel):
    """Modelo para propriedades do schema"""
    type: str
    description: Optional[str] = None
    enum: Optional[List[str]] = None
    items: Optional[Any] = None
    properties: Optional[Dict[str, 'PropertySchema']] = None
    required: Optional[List[str]] = None
    additionalProperties: Optional[bool] = None
    nullable: Optional[bool] = None
    
    class Config:
        extra = "allow"  # Permite campos adicionais


class ParametersSchema(BaseModel):
    """Modelo para o objeto parameters"""
    type: str = Field(default="object")
    required: List[str] = []
    properties: Dict[str, PropertySchema]
    additionalProperties: bool = Field(default=False)
    
    def enrich_with_nullable(self) -> 'ParametersSchema':
        """Adiciona nullable: true para campos não obrigatórios"""
        enriched_properties = {}
        
        for prop_name, prop_schema in self.properties.items():
            prop_dict = prop_schema.dict(exclude_none=True)
            
            # Se o campo não está em required, adiciona nullable: true
            if prop_name not in self.required:
                prop_dict['nullable'] = True
            
            enriched_properties[prop_name] = PropertySchema(**prop_dict)
        
        # Cria uma nova instância com as propriedades enriquecidas
        return ParametersSchema(
            type=self.type,
            required=self.required,
            properties=enriched_properties,
            additionalProperties=self.additionalProperties
        )
    
    def enrich_with_additional_properties(self) -> 'ParametersSchema':
        """Adiciona additionalProperties: False a todos os objetos"""
        def enrich_recursive(prop: PropertySchema) -> PropertySchema:
            """Função recursiva para enriquecer propriedades"""
            prop_dict = prop.dict(exclude_none=True)
            
            # Se é um objeto com properties, adiciona additionalProperties
            if prop_dict.get('type') == 'object' and 'properties' in prop_dict:
                if 'additionalProperties' not in prop_dict:
                    prop_dict['additionalProperties'] = False
                
                # Processa propriedades recursivamente
                if 'properties' in prop_dict:
                    enriched_sub_props = {}
                    for sub_name, sub_prop in prop_dict['properties'].items():
                        enriched_sub_props[sub_name] = enrich_recursive(
                            PropertySchema(**sub_prop)
                        )
                    prop_dict['properties'] = enriched_sub_props
            
            # Processa items em arrays
            if prop_dict.get('type') == 'array' and 'items' in prop_dict:
                if isinstance(prop_dict['items'], dict):
                    prop_dict['items'] = enrich_recursive(
                        PropertySchema(**prop_dict['items'])
                    )
            
            return PropertySchema(**prop_dict)
        
        # Enriquecer todas as propriedades
        enriched_properties = {}
        for prop_name, prop_schema in self.properties.items():
            enriched_properties[prop_name] = enrich_recursive(prop_schema)
        
        return ParametersSchema(
            type=self.type,
            required=self.required,
            properties=enriched_properties,
            additionalProperties=self.additionalProperties
        )


class FunctionSchema(BaseModel):
    """Modelo para o objeto function"""
    name: str
    description: str
    parameters: ParametersSchema
    strict: bool = False
    
    def enrich(self) -> 'FunctionSchema':
        """Aplica ambos os enriquecimentos"""
        # Primeiro, enriquecer com nullable
        params_with_nullable = self.parameters.enrich_with_nullable()
        
        # Depois, enriquecer com additionalProperties
        fully_enriched_params = params_with_nullable.enrich_with_additional_properties()
        
        return FunctionSchema(
            name=self.name,
            description=self.description,
            parameters=fully_enriched_params,
            strict=self.strict
        )


class FunctionCallSchema(BaseModel):
    """Modelo para o schema completo de chamada de função"""
    type: str = Field(default="function")
    function: FunctionSchema
    
    def enrich(self) -> 'FunctionCallSchema':
        """Aplica enriquecimento ao schema completo"""
        enriched_function = self.function.enrich()
        return FunctionCallSchema(type=self.type, function=enriched_function)
    
    def to_enriched_dict(self) -> Dict[str, Any]:
        """Retorna o dicionário enriquecido"""
        enriched = self.enrich()
        return enriched.dict(exclude_none=True)


# Funções utilitárias para processamento direto
def enrich_json_schema(json_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Função principal que enriquece o JSON schema com ambos os enriquecimentos
    """
    # Cria o modelo a partir do JSON
    try:
        function_schema = FunctionCallSchema(**json_data)
    except ValidationError as e:
        print(f"Erro de validação: {e}")
        return json_data
    
    # Aplica os enriquecimentos
    enriched_schema = function_schema.enrich()
    
    # Retorna como dicionário
    return enriched_schema.dict(exclude_none=True)


def enrich_json_schema_recursive(json_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Versão alternativa que processa recursivamente sem modelos Pydantic
    """
    def add_nullable(schema: Dict[str, Any]) -> Dict[str, Any]:
        """Adiciona nullable: true a campos não obrigatórios"""
        if not isinstance(schema, dict):
            return schema
        
        result = schema.copy()
        
        # Verifica se é um objeto com properties e required
        if (result.get('type') == 'object' and 
            'properties' in result and 
            'required' in result):
            
            required_fields = result['required']
            properties = result['properties']
            
            for field_name, field_props in properties.items():
                if field_name not in required_fields:
                    if isinstance(field_props, dict):
                        field_props['nullable'] = True
        
        return result
    
    def add_additional_properties(schema: Dict[str, Any]) -> Dict[str, Any]:
        """Adiciona additionalProperties: false a todos os objetos"""
        if not isinstance(schema, dict):
            return schema
        
        result = schema.copy()
        
        # Se for um objeto com properties, adiciona additionalProperties
        if result.get('type') == 'object' and 'properties' in result:
            if 'additionalProperties' not in result:
                result['additionalProperties'] = False
            
            # Processa propriedades recursivamente
            if 'properties' in result:
                for prop_name, prop_schema in result['properties'].items():
                    result['properties'][prop_name] = add_additional_properties(prop_schema)
        
        # Processa items em arrays
        if result.get('type') == 'array' and 'items' in result:
            result['items'] = add_additional_properties(result['items'])
        
        return result
    
    # Aplica os enriquecimentos em sequência
    with_nullable = add_nullable(json_data)
    fully_enriched = add_additional_properties(with_nullable)
    
    return fully_enriched


# Exemplo de uso
if __name__ == "__main__":
    # Exemplo 1: Primeiro JSON (add_comment_to_pending_review)
    json_example_1 = {
        'type': 'function',
        'function': {
            'name': 'add_comment_to_pending_review',
            'description': "Add review comment to the requester...ll this (check with the user if not sure).",
            'parameters': {
                'type': 'object',
                'required': ['owner', 'repo', 'pullNumber', 'path', 'body', 'subjectType'],
                'properties': {
                    'body': {
                        'type': 'string',
                        'description': 'The text of the review comment'
                    },
                    'line': {
                        'type': 'number',
                        'description': 'The line of the blob in the pull request diff that the comment applies to. For multi-line comments, the last line of the range'
                    },
                    'owner': {
                        'type': 'string',
                        'description': 'Repository owner'
                    },
                    'path': {
                        'type': 'string',
                        'description': 'The relative path to the file that necessitates a comment'
                    },
                    'pullNumber': {
                        'type': 'number',
                        'description': 'Pull request number'
                    },
                    'repo': {
                        'type': 'string',
                        'description': 'Repository name'
                    },
                    'side': {
                        'type': 'string',
                        'description': 'The side of the diff to comment on. LEFT indicates the previous state, RIGHT indicates the new state',
                        'enum': ['LEFT', 'RIGHT']
                    },
                    'startLine': {
                        'type': 'number',
                        'description': 'For multi-line comments, the first line of the range that the comment applies to'
                    },
                    'startSide': {
                        'type': 'string',
                        'description': 'For multi-line comments, the starting side of the diff that the comment applies to. L...vious state, RIGHT indicates the new state',
                        'enum': ['LEFT', 'RIGHT']
                    },
                    'subjectType': {
                        'type': 'string',
                        'description': 'The level at which the comment is targeted',
                        'enum': ['FILE', 'LINE']
                    }
                },
                'additionalProperties': False
            },
            'strict': False
        }
    }
    
    # Exemplo 2: Segundo JSON (push_files)
    json_example_2 = {
        'type': 'function',
        'function': {
            'name': 'push_files',
            'description': 'Push multiple files to a GitHub repository in a single commit',
            'parameters': {
                'type': 'object',
                'required': ['owner', 'repo', 'branch', 'files', 'message'],
                'properties': {
                    'branch': {
                        'type': 'string',
                        'description': 'Branch to push to'
                    },
                    'files': {
                        'type': 'array',
                        'description': 'Array of file objects to push, each object with path (string) and content (string)',
                        'items': {
                            'type': 'object',
                            'required': ['path', 'content'],
                            'properties': {
                                'content': {
                                    'type': 'string',
                                    'description': 'file content'
                                },
                                'path': {
                                    'type': 'string',
                                    'description': 'path to the file'
                                }
                            }
                        }
                    },
                    'message': {
                        'type': 'string',
                        'description': 'Commit message'
                    },
                    'owner': {
                        'type': 'string',
                        'description': 'Repository owner'
                    },
                    'repo': {
                        'type': 'string',
                        'description': 'Repository name'
                    }
                },
                'additionalProperties': False
            },
            'strict': True
        }
    }
    
    def test_enrichment(json_example: Dict[str, Any], example_name: str):
        """Testa o enriquecimento em um exemplo"""
        print(f"\n{'='*60}")
        print(f"Testando: {example_name}")
        print(f"{'='*60}")
        
        print("\nJSON Original:")
        print(json.dumps(json_example, indent=2))
        
        print("\n\nUsando Modelo Pydantic:")
        enriched_1 = enrich_json_schema(json_example)
        print(json.dumps(enriched_1, indent=2))
        
        print("\n\nUsando Função Recursiva:")
        enriched_2 = enrich_json_schema_recursive(json_example)
        print(json.dumps(enriched_2, indent=2))
        
        # Verifica se os resultados são iguais
        if enriched_1 == enriched_2:
            print(f"\n✓ Ambos os métodos produzem o mesmo resultado para {example_name}")
        else:
            print(f"\n✗ Os métodos produzem resultados diferentes para {example_name}")
        
        # Validação específica
        print(f"\nValidação para {example_name}:")
        
        # Verifica nullable
        params = enriched_1['function']['parameters']
        required = params['required']
        properties = params['properties']
        
        print(f"  Campos obrigatórios: {required}")
        for field_name, props in properties.items():
            is_required = field_name in required
            has_nullable = props.get('nullable') is True
            
            if not is_required and not has_nullable:
                print(f"  ✗ {field_name} não é obrigatório mas não tem nullable: true")
            elif is_required and has_nullable:
                print(f"  ✗ {field_name} é obrigatório mas tem nullable: true")
            else:
                print(f"  ✓ {field_name}: required={is_required}, nullable={has_nullable}")
        
        # Verifica additionalProperties em objetos aninhados
        def check_additional_props(node: Any, path: str = "") -> None:
            if isinstance(node, dict):
                if node.get('type') == 'object' and 'properties' in node:
                    current_path = f"{path}.object" if path else "object"
                    if 'additionalProperties' in node:
                        if node['additionalProperties'] == False:
                            print(f"  ✓ {current_path:50} tem additionalProperties: False")
                        else:
                            print(f"  ✗ {current_path:50} tem additionalProperties: {node['additionalProperties']} (deveria ser False)")
                    else:
                        print(f"  ✗ {current_path:50} não tem additionalProperties")
                
                for key, value in node.items():
                    new_path = f"{path}.{key}" if path else key
                    check_additional_props(value, new_path)
            elif isinstance(node, list):
                for i, item in enumerate(node):
                    check_additional_props(item, f"{path}[{i}]")
        
        print(f"\n  Verificando additionalProperties em objetos:")
        check_additional_props(enriched_1)
    
    # Testar ambos os exemplos
    test_enrichment(json_example_1, "add_comment_to_pending_review")
    test_enrichment(json_example_2, "push_files")
    
    # Exemplo de uso direto com o modelo Pydantic
    print(f"\n{'='*60}")
    print("Exemplo de uso direto com Pydantic:")
    print(f"{'='*60}")
    
    # Criar modelo a partir do JSON
    model = FunctionCallSchema(**json_example_2)
    
    # Aplicar enriquecimento
    enriched_model = model.enrich()
    
    # Obter dicionário enriquecido
    enriched_dict = enriched_model.to_enriched_dict()
    
    print("\nModelo original:", model.type)
    print("Nome da função:", model.function.name)
    print("\nModelo enriquecido gerado:")
    print(json.dumps(enriched_dict, indent=2))
    
    # Verificar o objeto dentro de files.items
    files_items = enriched_dict['function']['parameters']['properties']['files']['items']
    print(f"\nObjeto dentro de files.items:")
    print(f"  Tem additionalProperties? {'additionalProperties' in files_items}")
    print(f"  Valor: {files_items.get('additionalProperties')}")
    
    if files_items.get('additionalProperties') == False:
        print("  ✓ additionalProperties: False foi adicionado corretamente!")
    else:
        print("  ✗ additionalProperties: False NÃO foi adicionado!")
