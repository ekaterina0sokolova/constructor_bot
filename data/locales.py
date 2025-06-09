from typing import Dict

Lexicons: Dict[str, dict] = {
    # Russion localization
    "RU": {
        # buttons
        'delete_context_button': 'Очистить контекст',
        'my_assistants_button': 'Мои ассистенты',
        'assistant_settings_button': 'Инструкции и знания',
        'change_model_button': 'Сменить модель',
        'billing_button': 'Баланс и расходы',
        'memorize_context_command_button': 'При смене модели сохранять контекст диалога',
        'help_button': 'Помощь',
        'confirm_terms_button': 'Соглашаюсь с условиями',
        'terms_button': 'Пользовательское соглашение',
        'back_button': 'Назад/в диалог',
        'memorize_context_demo_button': '🔜Сохранять контекст (в разработке)',
        'telegram_subscription_button': 'Перейти на канал',
        'confirm_telegram_subscription_button': '✅ Я подписался на канал!',

        # messages
        'terms': 'Пожалуйста, ознакомьтесь с условиями использования бота',
        'telegram_subscription': '👋 Для того, чтобы пользоваться ботом, необходимо подписаться на наш канал.\n\nПродолжая использование бота, Вы соглашаетесь с [Пользовательским соглашением](https://worken.ai/user-agreement)\n\nПосле подписки, нажмите на соответствующую кнопку.',
        'hello_message': '''👋 Привет! Я здесь, чтобы помочь вам создать AI-ассистентов без VPN! \n\n💻 Вот что я могу вам предложить:\n-🛠 Создайте до 20 AI-ассистентов для разных задач..\n- ✨ Настройте их: дайте имя, описание, инструкции и выберите параметры ответов!\n-🧠 Узнайте возможности различных llm-моделей для общения.\n-💬 Общайтесь с вашим ассистентом в любое время!\n\nГотовы начать? Попробуйте создать своего первого AI-ассистента в разделе */my_assistants*  🚀\n\nПоддержка - @workenai\\_support\\_bot''',
        'wrong_subscription': 'Для использования этого инструмента необходимо приобрести подписку.',
        'wrong_tokens_amount': 'Похоже, что у вас недостаточно токенов.\nДля использования этой фукнции неоходимо иметь ненулевой баланс\n\nПополните баланс в разделе /billing',

        'delete_context_text': '✅ Контекст диалога удален.',
        'terms_text_url': 'https://worken.ai/ru',
        'assistant_name_length_err_text': 'Длина имени должна быть от 1 до 20 символов. Попробуйте ввести еще раз.',
        'assistant_instructions_length_err_text': 'Длина инструкций должна быть от 10 до 200 символов (временное ограничение). Попробуйте ввести еще раз.',
        'reached_max_assistant_cnt_text': 'Достигнуто максимальное количество ассистентов, чтобы создать нового асситента удалите одного из списка.',

        # My Assistans module
        'my_assistants_text': 'Выберите активного ассистента, который ответит вам прямо сейчас! \nИли создайте нового, чтобы он стал вашим верным помощником.',
        'no_assistants_text': 'У Вас пока нет ассистентов, создайте первого!',
        'create_assistant_button': '➕Создать ассистента',
        'as_back_button': 'Назад/в диалог',
        'new_assistant_button': 'К ассистентам',
        'new_assistant_form_text': 'Введите название для ассистента',
        'assistant_created': 'Вы создали нового ассистента!\n\nНачните общаться с ним прямо сейчас!',
        'enter_assistant_instructions_text': 'Напишите инструкции (роль) для ассистента',
        'create_assistant_canceled_text': 'Создание ассистента отменено',
        'continue_to_add_assistant_text': 'Пожалуйста, закончите создание ассистента',
        'delete_selected_assistant_button': '⚠️Удалить выбранного ассистента⚠️',
        'confirm_assistant_deletion_btn': '⚠️Удалить ассистента⚠️',

        # Имя ассистента
        'update_assistant_name_text': '''Назовите своего ассистента по-новому! \nВыберите новое название, которое будет уместно и легко запоминать. \nДлина названия не должна превышать *20 символов*. \n*старое название заменится на новое*''',
        'update_assistant_name_done': '''✅ Название изменено на: "{assistant_name}"''',

        # Описание ассистента
        'description_button_clicked': '''Дайте свою личную характеристику или описание своему ассистенту.\n\nЭто поможет вам отличить его от других и будет использоваться только в качестве вспомогательной информации. \n\n*Новое описание полностью заменит старое*''',

        'update_assistant_description_done': '''✅ Описание ассистента изменено!''',
        'assistant_description_length_err_text': '❌Описание ассистента введено неверно. Оно должно содержать до 200 символов. Попробуйте ввести снова.',

        # Инструкции (роль)
        'instructions_button_clicked': '''Введите новые инструкции''',
        'update_assistant_instructions_done': '''✅ Новые инструкции записаны!''',
        'assistant_instructions_length_err_text': '''❌Извините, но при введении новых инструкций превышено максимальное количество символов. \nПопробуйте еще раз! \n\nПожалуйста, убедитесь, что новая версия не превышает максимальную длину *1000 символов (включая пробелы)*. \n\nМы ждем ваших новых настроек!''',
        'delete_instructions_button_text': '⚠️ Удалить текущие инструкции',
        'instructions_deleted_text': '''✅ Инструкции успешно очищены!''',

        # Температура
        'temperature_button_clicked': '''Здесь вы можете изменить значение параметра «Температура ответов» для выбранной модели, подключенной к своему ассистенту. Это поможет вам настроить тон и стиль его реплик. \nВведите значение параметра температура *от 0 до 1 в формате 0.X, например: 0.6*''',
        'update_assistant_temperature_done': '''✅ Температура ответов изменена на: {temperature}.''',
        'assistant_temperature_err_text': '''❌Вы ввели неверное значение параметра *Температура ответов*. \nЭто значение должно быть от 0 до 2 в виде десятичной дроби с запятой.\nПопробуйте еще раз! \nВведите новое значение для своего ассистента. Например: 0.8''',

        # Top p
        'top_p_button_clicked': '''Вы можете изменить значение параметра Top P для выбранной модели, подключенной к ассистенту.  Значение должно быть от 0 до 1.\n\nПараметр Top P необходим для улучшения работы ассистента и обеспечения наиболее точных ответов на ваши вопросы.\n\nНапример, если вы хотите получить более детальную информацию о конкретном предмете, параметр Top P может помочь ассистенту предоставить вам больше информации. \n\nВведите значение от 0 до 1 в формате 0.Х *например: 0.6*''',
        'update_assistant_top_p_done': '''✅ Параметр Top P изменен на: {top_p}.''',
        'assistant_top_p_err_text': '❌Вы ввели неверные значения параметра. \nПараметр должен быть от 0 до 1 в виде десятичной дроби с точкой (например, 0.5 или 0.75). \nПожалуйста, попробуйте еще раз ввести значение.',

        # Assistant settings module
        'settings_module_text': '''Хотите сделать своего ассистента еще более персонализированным? \n\nИзмените его параметры прямо сейчас! \n\nТекущий ассистент: *{assistant_name}*.''',
        'pro_settings_module_text': '''Вы в модуле профеcсиональных настроек\n\nТекущий ассистент: *{assistant_name}*.''',
        'settings_module_name_button': '🏷️ Название',
        'settings_module_description_button': 'Описание',
        'settings_module_instructions_button': '📋 Инструкции',
        'settings_module_knowledge_base_button': '🔜Базы знаний (в разработке)',
        'settings_module_top_p_button': 'Top P',
        'settings_module_temperature_button': 'Температура ответов',
        'settings_module_tools_button': '🔜Тулзы (в разработке)',
        'instructions_module_text': '''Здесь Вы можете увидеть текущие инструкции для Вашего ассистента, удалить их или изменить.\n\n*Текущие инструкции:*\n{current_assistant_instructions}\n\nИнструкции:\n1. Помогают ассистенту понимать цель и задачи\n2. Улучшают реакцию ассистента на разные ситуации\n3. Позволяют ассистенту принимать решения в диалогах с пользователями''',
        'set_instructions_button_text': 'Задать новые инструкции',
        'pro_settings_text': '⚙️ Профессиональные настройки',

        # Базы знаний
        'create_storage_button': 'Добавить базу знаний',
        'save_user_choice_button': 'Сохранить мой выбор',

        # Change model module
        'change_model_module_text': '''Выберете одну из доступных llm моделей прямо сейчас!''',
        'next_models_button': 'больше моделей',

        # Balance and expenses
        'balance_module_text': 'Баланс и расходы',
        'pay_by_card_button': '💳Пополнить картой',
        'other_pay_button': 'Пополнить "с расчетного счета"',
        'cost_details_button': 'Детализация расходов',
        'replenishment_history_button': '📃История пополнений',

        # Виды "покупок"
        'credits': 'Токены',
        'subscription': 'Подписка',



        # Memorize context module
        'memorize_context_text': '''🔜(в разарботке)\nКогда вы включаете функцию "Сохранение контекста", модель ассистента запоминает историю вашего общения и может использовать эту информацию при ответах на будущие вопросы.\n\nЧтобы включить или выключить функцию сохранения контекста, просто нажмите кнопку ниже. \n\nПожалуйста, помните о том, что сохранение контекста может потребовать больше токенов для использования.''',
        'memorize_context_true_button': 'Сохранять контекст ✅',
        'memorize_context_false_button': 'Сохранять контекст ❌',
        'memorize_context_button': 'Сохранять контекст диалога',

        # Help module
        'help_module_text': '''Что-то пошло не так? Мы здесь, чтобы помочь!\n\nВы зашли в пункт "Помощь", потому что хотели узнать больше о возможностях нашего бота. И мы рады предоставить вам эту информацию!\n\nДавайте начнем с основных команд и функций:\n*/my_assistants* - если хотите *выбрать/создать/удалить ассистента*.\n\n*/assistant_settings* - если хотите *изменить настройки* текущего ассистента\n\n*/delete_context* - если хотите *очистить контекст диалога* с текущим ассистентом\n\n*/change_model* - если хотите *поменять llm-модель* для текущего ассистента\n\n*/billing* - если хотите *узнать/пополнить баланс, посмотреть историю пополнений*\n\n🔜*/memorize_context* - если хотите *включть/выключить сохранение контекста диалога*\n\n*/help* - если хотите *узнать про основные команды бота* или написать в поддержку\n\nЕсли у вас более сложный вопрос или вы не нашли ответа на него в этом сообщении, нажмите кнопку "Поддержка" ниже. \n\nМы будем рады помочь вам как можно скорее! Наша команда поддержки работает круглосуточно и готова решить любую проблему с нашей платформой.\n\nМы ответим вам в самое ближайшее время, чтобы разобраться в ситуации и помочь вам. \n\nСпасибо за выбор нашей платформы!''',
        'suppport_button': 'Поддержка',
      },

    # English localization
    "EN": {
        # buttons
        'delete_context_button': 'Delete context',
        'my_assistants_button': 'My assistans',
        'assistant_settings_button': 'Instructions and knowledge',
        'change_model_button': 'Change model',
        'billing_button': 'Balance and expenses',
        'memorize_context_command_button': 'When changing the model, save the dialog context',
        'help_button': 'Help',
        'confirm_terms_button': 'Confirm',
        'terms_button_button': 'Terms',

        # messages
        'terms': 'Please read our terms of use.',
        'hello_message': '*Hello from bot',
        'delete_context_text': 'The context has been deleted',

        # My Assistans Module
        'my_assistants_text': 'You are now in My Assistans module',
        'create_assistant_button': 'Create new assistant',
        'as_back_button': 'Back',
        'new_assistant_button': 'Done',
        'new_assistant_form_text': '* New Assistant Form',
      },
  }