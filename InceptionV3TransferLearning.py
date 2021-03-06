import numpy as np
import matplotlib.pyplot as plt
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential
from keras.layers import Dropout, Flatten, Dense, GlobalAveragePooling2D
from keras import applications
from keras import regularizers
from keras import optimizers

img_width, img_height = 299, 299

top_model_weights_path = "isic-inceptionV3-transfer-learning.h5"

train_data_dir = '/home/openroot/Tanmoy/Working Stuffs/myStuffs/havss-tf/ISIC-2017/data/train'
validation_data_dir = '/home/openroot/Tanmoy/Working Stuffs/myStuffs/havss-tf/ISIC-2017/data/validation'

train_aug_data_dir = '/home/openroot/Tanmoy/Working Stuffs/myStuffs/havss-tf/ISIC-2017/data/aug/train'
validation_aug_data_dir = "/home/openroot/Tanmoy/Working Stuffs/myStuffs/havss-tf/ISIC-2017/data/aug/validation"

nb_train_samples = 9216
nb_validation_samples = 2304

epochs = 50

batch_size = 32


def saveBottleneckTransferValues():
    # VGG16 Model
    # model = applications.VGG16(include_top = False, weights = "imagenet")

    # Inception V3
    model = applications.inception_v3.InceptionV3(include_top = False, weights = "imagenet")

    datagen = ImageDataGenerator(
        rescale = 1./255
    )

    # Training
    train_datagen = ImageDataGenerator(
        rescale = 1./255,
        # rotation_range = 40,
        # width_shift_range = 0.1,
        # height_shift_range = 0.1,
        # shear_range = 0.1,
        # zoom_range = 0.1,
        # horizontal_flip = True,
        # fill_mode = "nearest"
    )

    train_generator = train_datagen.flow_from_directory(
        train_aug_data_dir,
        target_size = (img_height, img_width),
        batch_size = batch_size,
        class_mode = None,
        shuffle = False
    )

    train_transfer_values = model.predict_generator(
        train_generator,
        nb_train_samples // batch_size
    )

    print("Train Transfer Values Shape : {0} ".format(train_transfer_values.shape))

    np.save(open("train-transfer-values-incepV3.npy", "w"), train_transfer_values)


    # Validation
    validation_datagen = ImageDataGenerator(
        rescale=1./255
    )    

    validation_generator = validation_datagen.flow_from_directory(
        validation_aug_data_dir,
        target_size = (img_height, img_width),
        batch_size = batch_size,
        class_mode = None,
        shuffle = False
    )

    validation_transfer_values = model.predict_generator(
        validation_generator,
        nb_validation_samples // batch_size 
    )

    print("Validation Transfer Value Shape : {0}".format(validation_transfer_values.shape))

    np.save(open("validation-tansfer-values-incepV3.npy", "w"), validation_transfer_values)


def trainTopModel():
    train_data = np.load(open("train-transfer-values-incepV3.npy"))
    train_labels = np.array( [0] *  (nb_train_samples / 2) + [1] * (nb_train_samples / 2))

    validation_data = np.load(open("validation-tansfer-values-incepV3.npy"))
    validation_labels = np.array( [0] * (nb_validation_samples / 2) + [1] * (nb_validation_samples / 2))

    model = Sequential()
    model.add(Flatten(input_shape = train_data.shape[1:]))
    # model.add(Dense(512, activation = "relu"))
    # model.add(Dropout(0.7))
    model.add(Dense(256, activation = "relu"))
    model.add(Dropout(0.7))
    model.add(Dense(1, activation = "sigmoid"))


    # model.compile(optimizer = "rmsprop", 
    #     loss = "binary_crossentropy", 
    #     metrics = ["accuracy"]
    # )

    model.compile(loss='binary_crossentropy',
        optimizer=optimizers.SGD(lr=1e-4, momentum=0.9),
        metrics=['accuracy']
    )

    # model.compile(optimizer='nadam',
    #     loss='binary_crossentropy',
    #     metrics=['accuracy']
    # )

    # model.compile(optimizer = "adam", 
    #     loss = "binary_crossentropy", 
    #     metrics = ["accuracy"]
    # )    

    history = model.fit(train_data, train_labels, 
        epochs = epochs, 
        batch_size = batch_size, 
        validation_data = (validation_data, validation_labels)
    )

    # list all data in history
    print(history.history.keys())


    # summarize history for accuracy
    plt.plot(history.history['acc'])
    plt.plot(history.history['val_acc'])
    plt.title('model accuracy')
    plt.ylabel('accuracy')
    plt.xlabel('epoch')
    plt.legend(['train', 'test'], loc='upper left')
    plt.show()


    # summarize history for loss
    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.title('model loss')
    plt.ylabel('loss')
    plt.xlabel('epoch')
    plt.legend(['train', 'test'], loc='upper left')
    plt.show()

    model.save_weights(top_model_weights_path)

def main():
    # saveBottleneckTransferValues()
    trainTopModel()

if __name__ == '__main__':
    main()